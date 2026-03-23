import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail
from app.conexion import conexion_DB
from app.usuario import Usuario
from app.perfil_model import PerfilUsuario
from app.precios_model import PreciosMateriales
from app.mapa_model import PuntosAcopio
from app.clasificador import ClasificadorResiduos
from app.historial_model import Historial
from app.graficas_model import GraficasDashboard
from app.recuperacion_model import RecuperacionPassword
from app.tickets_model import Tickets
from app.admin_model import Admin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'app', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'app', 'static'))

app.secret_key = 'ecovision_secret_key_2024'

# ── Configuración Gmail ────────────────────────────────────────────────────
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('EcoVision AI', os.environ.get('MAIL_USERNAME'))

mail = Mail(app)

# ── Conexión BD ────────────────────────────────────────────────────────────
db = conexion_DB(app)
usuario_ctrl     = Usuario(db.conexion)
perfil_ctrl      = PerfilUsuario(db.conexion)
precios_ctrl     = PreciosMateriales()
mapa_ctrl        = PuntosAcopio()
clasificador_ctrl = ClasificadorResiduos()
historial_ctrl   = Historial(db.conexion)
graficas_ctrl    = GraficasDashboard(db.conexion)
recuperacion_ctrl = RecuperacionPassword(db.conexion, mail)
tickets_ctrl      = Tickets(db.conexion)
admin_ctrl        = Admin(db.conexion)


# ── Utilidad: verificar sesión activa ──────────────────────────────────────
def sesion_activa():
    return 'usuario_id' in session

def es_admin():
    return session.get('usuario_rol') == 'admin'

# ── Middleware: verificar modo mantenimiento ───────────────────────────────
@app.before_request
def verificar_mantenimiento():
    rutas_libres = ['login', 'registro', 'olvide_password',
                    'recuperar_password', 'static', 'admin_panel',
                    'admin_tickets_estado', 'admin_eliminar_usuario',
                    'admin_mantenimiento']
    if request.endpoint in rutas_libres:
        return
    if es_admin():
        return
    if admin_ctrl.obtener_mantenimiento():
        return render_template('mantenimiento.html'), 503


# ── Utilidad: obtener estadísticas del usuario ────────────────────────────
def obtener_stats(usuario_id):
    try:
        cur = db.conexion.connection.cursor()
        cur.execute('''
            SELECT
                COUNT(*)                        AS clasificados,
                ROUND(SUM(peso_kg), 1)          AS kg,
                COUNT(DISTINCT tipo_material)   AS materiales
            FROM historial
            WHERE usuario_id = %s
        ''', (usuario_id,))
        row = cur.fetchone()
        cur.close()
        return {
            'clasificados': row['clasificados'] or 0,
            'kg':           row['kg'] or 0,
            'materiales':   row['materiales'] or 0
        }
    except Exception:
        return {'clasificados': 0, 'kg': 0, 'materiales': 0}


# ── Rutas de autenticación ─────────────────────────────────────────────────

@app.route('/')
def index():
    if sesion_activa():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if sesion_activa():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        resultado = usuario_ctrl.autenticar(
            request.form.get('email', ''),
            request.form.get('password', '')
        )
        if resultado['ok']:
            session['usuario_id']    = resultado['id']
            session['usuario_nombre']= resultado['usuario']
            session['usuario_rol']   = resultado.get('rol', 'usuario')
            if session['usuario_rol'] == 'admin':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        flash(resultado['msg'], 'error')
    return render_template('login.html', tab_activo='login')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if sesion_activa():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        resultado = usuario_ctrl.registrar(
            request.form.get('usuario', ''),
            request.form.get('email', ''),
            request.form.get('password', ''),
            request.form.get('confirmar', '')
        )
        if resultado['ok']:
            flash(resultado['msg'], 'success')
            return redirect(url_for('login'))
        flash(resultado['msg'], 'error')
    return render_template('login.html', tab_activo='registro')


# ── Dashboard ──────────────────────────────────────────────────────────────

@app.route('/dashboard')
def dashboard():
    if not sesion_activa():
        return redirect(url_for('login'))
    stats = obtener_stats(session['usuario_id'])
    return render_template('dashboard.html',
                            nombre=session['usuario_nombre'],
                            stats=stats)


@app.route('/estadisticas')
def estadisticas():
    if not sesion_activa():
        return redirect(url_for('login'))
    uid = session['usuario_id']
    stats_hist = historial_ctrl.obtener_stats(uid)
    stats_hist['clasificados'] = stats_hist['total']
    graficas = {
        'semanal':    graficas_ctrl.actividad_semanal(uid),
        'materiales': graficas_ctrl.materiales_distribucion(uid)
    }
    return render_template('estadisticas.html',
                            nombre=session['usuario_nombre'],
                            stats=stats_hist,
                            graficas=graficas)


# ── Módulos (rutas vacías por ahora, se llenarán en los siguientes pasos) ──

@app.route('/clasificador')
def clasificador():
    if not sesion_activa():
        return redirect(url_for('login'))
    return render_template('clasificador.html', nombre=session['usuario_nombre'])


@app.route('/clasificador/guardar', methods=['POST'])
def clasificador_guardar():
    from flask import jsonify
    if not sesion_activa():
        return jsonify({'ok': False, 'msg': 'Sesión expirada'}), 401
    datos = request.get_json()
    resultado = clasificador_ctrl.guardar_historial(
        db.conexion, session['usuario_id'], datos
    )
    return jsonify(resultado)


@app.route('/precios')
def precios():
    if not sesion_activa():
        return redirect(url_for('login'))
    lista     = precios_ctrl.obtener_todos()
    top       = lista[0] if lista else {'nombre': '-', 'precio_kg': 0}
    return render_template('precios.html',
                            nombre=session['usuario_nombre'],
                            materiales=lista,
                            top_nombre=top['nombre'],
                            top_precio=top['precio_kg'],
                            total=len(lista),
                            fecha_hoy=precios_ctrl.fecha_hoy())


@app.route('/mapa')
def mapa():
    if not sesion_activa():
        return redirect(url_for('login'))
    return render_template('mapa.html',
                            nombre=session['usuario_nombre'],
                            puntos=mapa_ctrl.obtener_todos())


@app.route('/historial')
def historial():
    if not sesion_activa():
        return redirect(url_for('login'))
    registros = historial_ctrl.obtener_registros(session['usuario_id'])
    stats     = historial_ctrl.obtener_stats(session['usuario_id'])
    return render_template('historial.html',
                            nombre=session['usuario_nombre'],
                            registros=registros,
                            stats=stats)


@app.route('/perfil')
def perfil():
    if not sesion_activa():
        return redirect(url_for('login'))
    usuario = perfil_ctrl.obtener(session['usuario_id'])
    stats   = obtener_stats(session['usuario_id'])
    return render_template('perfil.html',
                            nombre=session['usuario_nombre'],
                            usuario=usuario,
                            stats=stats)


@app.route('/perfil/actualizar', methods=['POST'])
def perfil_actualizar():
    if not sesion_activa():
        return redirect(url_for('login'))
    resultado = perfil_ctrl.actualizar(
        session['usuario_id'],
        request.form.get('ciudad', ''),
        request.form.get('password', ''),
        request.form.get('confirmar', '')
    )
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('perfil'))


@app.route('/perfil/avatar', methods=['POST'])
def perfil_avatar():
    if not sesion_activa():
        return redirect(url_for('login'))
    archivo   = request.files.get('avatar')
    resultado = perfil_ctrl.actualizar_avatar(session['usuario_id'], archivo)
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('perfil'))


# ── Logout ─────────────────────────────────────────────────────────────────

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))


# ── Recuperación de contraseña ────────────────────────────────────────────

@app.route('/olvide-password', methods=['GET', 'POST'])
def olvide_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not recuperacion_ctrl.email_existe(email):
            flash('Si ese correo está registrado, recibirás un enlace en breve.', 'success')
            return redirect(url_for('olvide_password'))
        resultado = recuperacion_ctrl.guardar_token(email)
        if resultado['ok']:
            base_url = request.host_url.rstrip('/')
            recuperacion_ctrl.enviar_email(email, resultado['token'], base_url)
        flash('Si ese correo está registrado, recibirás un enlace en breve.', 'success')
        return redirect(url_for('olvide_password'))
    return render_template('olvide_password.html')


@app.route('/recuperar/<token>', methods=['GET', 'POST'])
def recuperar_password(token):
    verificacion = recuperacion_ctrl.verificar_token(token)
    if not verificacion['ok']:
        flash(verificacion['msg'], 'error')
        return redirect(url_for('olvide_password'))
    if request.method == 'POST':
        resultado = recuperacion_ctrl.cambiar_password(
            token,
            request.form.get('password', ''),
            request.form.get('confirmar', '')
        )
        if resultado['ok']:
            flash(resultado['msg'], 'success')
            return redirect(url_for('login'))
        flash(resultado['msg'], 'error')
    return render_template('nueva_password.html', token=token)


# ── Panel Admin ────────────────────────────────────────────────────────────

@app.route('/admin')
def admin_panel():
    if not sesion_activa() or not es_admin():
        return redirect(url_for('login'))
    return render_template('admin_panel.html',
                            nombre=session['usuario_nombre'],
                            stats=admin_ctrl.obtener_stats_globales(),
                            tickets=tickets_ctrl.obtener_todos(),
                            usuarios=admin_ctrl.obtener_usuarios(),
                            mantenimiento=admin_ctrl.obtener_mantenimiento())


@app.route('/admin/tickets/<int:ticket_id>/estado', methods=['POST'])
def admin_tickets_estado(ticket_id):
    if not sesion_activa() or not es_admin():
        return redirect(url_for('login'))
    estado    = request.form.get('estado', '')
    resultado = tickets_ctrl.actualizar_estado(ticket_id, estado)
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('admin_panel') + '#sec-tickets')


@app.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
def admin_eliminar_usuario(usuario_id):
    if not sesion_activa() or not es_admin():
        return redirect(url_for('login'))
    resultado = admin_ctrl.eliminar_usuario(usuario_id)
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('admin_panel') + '#sec-usuarios')


@app.route('/admin/mantenimiento', methods=['POST'])
def admin_mantenimiento():
    if not sesion_activa() or not es_admin():
        return redirect(url_for('login'))
    resultado = admin_ctrl.toggle_mantenimiento()
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('admin_panel') + '#sec-config')


# ── Tickets / Mesa de ayuda ────────────────────────────────────────────────

@app.route('/mis-tickets')
def mis_tickets():
    if not sesion_activa():
        return redirect(url_for('login'))
    tickets = tickets_ctrl.obtener_por_usuario(session['usuario_id'])
    return render_template('mis_tickets.html',
                            nombre=session['usuario_nombre'],
                            tickets=tickets,
                            tipos=tickets_ctrl.TIPOS)


@app.route('/tickets/crear', methods=['POST'])
def tickets_crear():
    if not sesion_activa():
        return redirect(url_for('login'))
    resultado = tickets_ctrl.crear(
        session['usuario_id'],
        request.form.get('tipo', ''),
        request.form.get('descripcion', ''),
        request.form.get('prioridad', 'baja')
    )
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('mis_tickets'))


# ── Página 404 personalizada ───────────────────────────────────────────────

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404


# ── Inicio ─────────────────────────────────────────────────────────────────



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)