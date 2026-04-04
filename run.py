import os
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

# ══════════════════════════════════════════════════════════════════
#  IMPORTACIONES — ¿Qué traemos?
#
#  De Flask traemos las herramientas principales:
#    · render_template → devuelve una página HTML al usuario
#    · request         → lee datos del formulario o la URL
#    · redirect        → manda al usuario a otra página
#    · url_for         → genera la URL de una función por su nombre
#    · session         → guarda datos del usuario entre páginas
#                        (como "¿quién está logueado?")
#    · flash           → muestra mensajes temporales tipo toast
#
#  Los "from app.xxx" son módulos propios del proyecto.
#  Cada uno encapsula la lógica de una parte específica.
#  Esto se llama SEPARACIÓN DE RESPONSABILIDADES — app.py
#  solo enruta, y los módulos hacen el trabajo real.
# ══════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════════
#  CREACIÓN DE LA APP FLASK
#
#  Flask necesita saber dónde están los HTML (templates)
#  y los archivos estáticos (CSS, imágenes, JS).
#  Los apuntamos a las carpetas correctas dentro de /app/.
# ══════════════════════════════════════════════════════════════════
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'app', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'app', 'static'))

# ══════════════════════════════════════════════════════════════════
#  SECRET KEY — Clave secreta de la app
#
#  Flask firma las cookies de sesión con esta clave.
#  Sin ella nadie puede falsificar la sesión de otro usuario.
#  En producción real NUNCA se deja en el código — va en una
#  variable de entorno. Aquí está así solo para desarrollo.
# ══════════════════════════════════════════════════════════════════
app.secret_key = 'ecovision_secret_key_2024'

# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE CORREO (Gmail)
#
#  Permite enviar emails desde la app (ej: recuperar contraseña).
#  Las credenciales vienen de VARIABLES DE ENTORNO
#  (os.environ.get) — buena práctica de seguridad.
#  Las contraseñas NUNCA se escriben directamente en el código.
# ══════════════════════════════════════════════════════════════════
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('EcoVision AI', os.environ.get('MAIL_USERNAME'))

mail = Mail(app)

# ══════════════════════════════════════════════════════════════════
#  CONEXIÓN A BASE DE DATOS + CONTROLADORES
#
#  Primero se crea la conexión a MySQL.
#  Luego se crean los "controladores": objetos que saben
#  cómo hacer operaciones en la BD (registrar usuario,
#  guardar historial, etc.).
#
#  Todos reciben db.conexion — esto se llama INYECCIÓN DE
#  DEPENDENCIAS: la conexión se pasa desde afuera, no se
#  crea dentro de cada clase. Facilita el mantenimiento.
# ══════════════════════════════════════════════════════════════════
db = conexion_DB(app)
usuario_ctrl      = Usuario(db.conexion)
perfil_ctrl       = PerfilUsuario(db.conexion)
precios_ctrl      = PreciosMateriales()
mapa_ctrl         = PuntosAcopio()
clasificador_ctrl = ClasificadorResiduos()
historial_ctrl    = Historial(db.conexion)
graficas_ctrl     = GraficasDashboard(db.conexion)
recuperacion_ctrl = RecuperacionPassword(db.conexion, mail)
tickets_ctrl      = Tickets(db.conexion)
admin_ctrl        = Admin(db.conexion)


# ══════════════════════════════════════════════════════════════════
#  FUNCIONES UTILITARIAS — Reutilizables en toda la app
#
#  sesion_activa() → ¿El usuario está logueado?
#  es_admin()      → ¿El usuario logueado es administrador?
#
#  Se reutilizan al inicio de casi cada ruta para
#  controlar el acceso. Evitan repetir la misma lógica.
# ══════════════════════════════════════════════════════════════════
def sesion_activa():
    return 'usuario_id' in session

def es_admin():
    return session.get('usuario_rol') == 'admin'

# ══════════════════════════════════════════════════════════════════
#  MIDDLEWARE — before_request
#
#  Este decorador hace que esta función se ejecute ANTES
#  de cada petición HTTP que llegue a la app.
#
#  Revisa si el admin activó el "modo mantenimiento".
#  Si está activo, bloquea el acceso a usuarios normales
#  y les muestra una página de mantenimiento (código 503).
#
#  503 = código HTTP estándar para "servicio no disponible".
#  Las rutas en "rutas_libres" siempre pueden abrirse
#  (login, registro, etc.) para que nadie quede encerrado.
# ══════════════════════════════════════════════════════════════════
@app.before_request
def verificar_mantenimiento():
    rutas_libres = ['login', 'registro', 'olvide_password',
                    'recuperar_password', 'static', 'admin_panel',
                    'admin_tickets_estado', 'admin_eliminar_usuario',
                    'admin_mantenimiento', 'index']
    if request.endpoint in rutas_libres:
        return
    if sesion_activa() and es_admin():
        return
    if admin_ctrl.obtener_mantenimiento():
        return render_template('mantenimiento.html'), 503


# ══════════════════════════════════════════════════════════════════
#  FUNCIÓN AUXILIAR — obtener_stats
#
#  Ejecuta una query SQL para contar cuántos residuos
#  ha clasificado el usuario, cuántos kilos, y cuántos
#  tipos de material distintos.
#
#  Retorna un diccionario con esos 3 valores.
#  Si algo falla, retorna ceros para no romper la app.
# ══════════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════════
#  RUTAS DE AUTENTICACIÓN
#
#  Una RUTA es una función que responde cuando el usuario
#  entra a una URL específica. El decorador @app.route(...)
#  es el que conecta la URL con la función.
#
#  Hay dos métodos HTTP importantes:
#    · GET  → el usuario solo cargó la página (ver formulario)
#    · POST → el usuario envió un formulario (procesar datos)
# ══════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    # Ruta raíz: si ya está logueado va al dashboard,
    # si no, al login.
    if sesion_activa():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # GET  → mostrar el formulario de login
    # POST → procesar las credenciales enviadas
    if sesion_activa():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        resultado = usuario_ctrl.autenticar(
            request.form.get('email', ''),
            request.form.get('password', '')
        )
        if resultado['ok']:
            # Guardamos datos del usuario en la SESSION.
            # La sesión persiste entre páginas gracias a
            # una cookie firmada con el secret_key.
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
    # GET  → mostrar el formulario de registro
    # POST → crear la cuenta con los datos del formulario
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
            # flash guarda el mensaje en la sesión.
            # El mensaje aparece UNA SOLA VEZ en el próximo
            # render. Luego desaparece (por eso se llama "flash").
            flash(resultado['msg'], 'success')
            return redirect(url_for('login'))
        flash(resultado['msg'], 'error')
    return render_template('login.html', tab_activo='registro')


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD Y ESTADÍSTICAS
#
#  Patrón de protección de rutas: si el usuario NO está
#  logueado, se le manda al login. Esto se repite en
#  casi todas las rutas de la app.
# ══════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════
#  CLASIFICADOR DE RESIDUOS
#
#  Tiene DOS rutas:
#
#  1. /clasificador (GET) → muestra la página con el
#     formulario para subir una imagen.
#
#  2. /clasificador/guardar (POST) → recibe datos en
#     formato JSON (no formulario HTML). Esto indica que
#     el frontend usa JavaScript para enviar la petición
#     (AJAX). La ruta responde con jsonify() en lugar de
#     HTML — es una mini API REST dentro de la app.
# ══════════════════════════════════════════════════════════════════

@app.route('/clasificador')
def clasificador():
    if not sesion_activa():
        return redirect(url_for('login'))
    return render_template('clasificador.html', nombre=session['usuario_nombre'])


@app.route('/clasificador/guardar', methods=['POST'])
def clasificador_guardar():
    from flask import jsonify
    # Si la sesión expiró, devolvemos error 401 en JSON
    # (no redirigimos porque esta ruta la llama JavaScript, no el navegador)
    if not sesion_activa():
        return jsonify({'ok': False, 'msg': 'Sesión expirada'}), 401
    datos = request.get_json()
    resultado = clasificador_ctrl.guardar_historial(
        db.conexion, session['usuario_id'], datos
    )
    return jsonify(resultado)


# ══════════════════════════════════════════════════════════════════
#  MÓDULOS INFORMATIVOS
#  Precios y mapa son rutas simples de solo lectura.
#  Solo verifican sesión, obtienen datos y renderizan HTML.
# ══════════════════════════════════════════════════════════════════

@app.route('/precios')
def precios():
    if not sesion_activa():
        return redirect(url_for('login'))
    lista = precios_ctrl.obtener_todos()
    top   = lista[0] if lista else {'nombre': '-', 'precio_kg': 0}
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


# ══════════════════════════════════════════════════════════════════
#  PERFIL DE USUARIO
#
#  Tres rutas separadas para el perfil:
#    · /perfil           → ver el perfil (GET)
#    · /perfil/actualizar → cambiar ciudad o contraseña (POST)
#    · /perfil/avatar    → subir foto de perfil (POST con archivo)
#
#  Después de cada POST se hace redirect (patrón PRG:
#  Post → Redirect → Get). Esto evita que recargar la
#  página envíe el formulario de nuevo accidentalmente.
# ══════════════════════════════════════════════════════════════════

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
    # request.files lee archivos enviados por el formulario
    archivo   = request.files.get('avatar')
    resultado = perfil_ctrl.actualizar_avatar(session['usuario_id'], archivo)
    flash(resultado['msg'], 'success' if resultado['ok'] else 'error')
    return redirect(url_for('perfil'))


# ══════════════════════════════════════════════════════════════════
#  LOGOUT
#
#  session.clear() borra TODOS los datos de la sesión.
#  El usuario queda deslogueado inmediatamente.
# ══════════════════════════════════════════════════════════════════

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))


# ══════════════════════════════════════════════════════════════════
#  RECUPERACIÓN DE CONTRASEÑA
#
#  Flujo completo en 2 pasos:
#
#  PASO 1 — /olvide-password
#    El usuario ingresa su email. Si existe en la BD,
#    se genera un TOKEN único y se envía por email.
#    Siempre se muestra el mismo mensaje (aunque el email
#    no exista) para no revelar qué cuentas están registradas.
#
#  PASO 2 — /recuperar/<token>
#    <token> es una VARIABLE DE URL — Flask extrae ese
#    valor de la URL y lo pasa como argumento a la función.
#    Si el token es válido y no expiró, el usuario puede
#    ingresar su nueva contraseña.
# ══════════════════════════════════════════════════════════════════

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
    # Verificamos que el token exista y no haya expirado
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


# ══════════════════════════════════════════════════════════════════
#  PANEL DE ADMINISTRACIÓN
#
#  Doble verificación de acceso: sesion_activa() AND es_admin().
#  Si alguien escribe /admin en la URL sin ser admin,
#  lo mandan al login sin revelar que la ruta existe.
#
#  Incluye tres acciones de admin:
#    · Cambiar estado de tickets de soporte
#    · Eliminar usuarios
#    · Activar/desactivar modo mantenimiento
# ══════════════════════════════════════════════════════════════════

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
    # <int:ticket_id> → Flask convierte automáticamente ese
    # segmento de la URL a un número entero (int).
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


# ══════════════════════════════════════════════════════════════════
#  TICKETS / MESA DE AYUDA
#
#  Permite a los usuarios crear tickets de soporte y
#  ver el estado de los que ya enviaron.
# ══════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════
#  MANEJO DE ERRORES
#
#  En lugar del error genérico de Flask, mostramos una
#  página 404 personalizada y amigable.
#
#  El segundo valor (404) es el CÓDIGO HTTP de respuesta.
#  Códigos importantes:
#    200 = OK (respuesta exitosa)
#    302 = redirect
#    401 = no autorizado
#    404 = página no encontrada
#    503 = servicio no disponible
# ══════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('404.html'), 404


# ══════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
#
#  Este bloque solo se ejecuta si corres el archivo
#  directamente con: python app.py
#
#  debug=True  → recarga automáticamente al guardar cambios
#  host='0.0.0.0' → acepta conexiones desde cualquier IP
#                   (necesario para correr en contenedores)
#  port=5000   → puerto donde escucha la app
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)