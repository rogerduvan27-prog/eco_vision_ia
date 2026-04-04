import re
from werkzeug.security import generate_password_hash, check_password_hash

# ══════════════════════════════════════════════════════════════════
#  IMPORTACIONES
#
#  · re → módulo de expresiones regulares (regex). Se usa para
#    validar que el email tenga el formato correcto.
#
#  · werkzeug.security → librería de seguridad de Flask.
#    generate_password_hash → convierte la contraseña en un hash
#                             irreversible antes de guardarla en BD.
#    check_password_hash   → verifica si una contraseña coincide
#                             con su hash sin necesidad de revertirlo.
#
#  CONCEPTO CLAVE — Hashing de contraseñas:
#  NUNCA se guardan contraseñas en texto plano en la BD.
#  Un hash es una transformación irreversible. Si alguien roba
#  la BD, solo ve hashes imposibles de revertir.
# ══════════════════════════════════════════════════════════════════


class Usuario:
    # ══════════════════════════════════════════════════════════════
    #  CLASE USUARIO — Controlador de autenticación
    #
    #  Una CLASE es un molde para crear objetos con sus propios
    #  datos y comportamientos agrupados en un solo lugar.
    #
    #  Este controlador tiene UNA sola responsabilidad:
    #  todo lo relacionado con usuarios (registrar, autenticar).
    #  No sabe nada de HTML ni de rutas — solo trabaja con datos.
    #  Esto se llama PRINCIPIO DE RESPONSABILIDAD ÚNICA (SRP).
    # ══════════════════════════════════════════════════════════════

    def __init__(self, mysql):
        # ──────────────────────────────────────────────────────────
        #  CONSTRUCTOR — Se ejecuta automáticamente al hacer:
        #  usuario_ctrl = Usuario(db.conexion) en app.py
        #
        #  Recibe la conexión a MySQL y la guarda en self.mysql
        #  para que todos los métodos de la clase puedan usarla.
        #
        #  Esto se llama INYECCIÓN DE DEPENDENCIAS: la conexión
        #  se recibe desde afuera, no se crea aquí adentro.
        #  Ventaja: si cambias la BD, solo cambias un lugar.
        # ──────────────────────────────────────────────────────────
        self.mysql = mysql

    # ── Validaciones privadas ──────────────────────────────────────────────

    def _email_valido(self, email: str) -> bool:
        # ──────────────────────────────────────────────────────────
        #  MÉTODO PRIVADO — El guion bajo (_) al inicio es una
        #  convención en Python que indica "solo para uso interno
        #  de esta clase". No se llama desde app.py.
        #
        #  Usa una EXPRESIÓN REGULAR (regex) para validar el email.
        #  El patrón r'^[\w.\-]+@[\w.\-]+\.\w{2,}$' verifica que:
        #    · Empiece con letras/números/puntos/guiones
        #    · Tenga un @
        #    · Tenga un dominio (algo.com, algo.co, etc.)
        #
        #  re.match devuelve un objeto si hay coincidencia, o None
        #  si no. bool() lo convierte a True/False.
        # ──────────────────────────────────────────────────────────
        return bool(re.match(r'^[\w.\-]+@[\w.\-]+\.\w{2,}$', email))

    def _password_valida(self, password: str) -> bool:
        # Regla mínima: al menos 8 caracteres.
        # En producción se podrían agregar más reglas
        # (mayúsculas, números, caracteres especiales, etc.)
        return len(password) >= 8

    def _usuario_valido(self, usuario: str) -> bool:
        # El nombre de usuario debe tener mínimo 3 caracteres
        # y no puede contener espacios (para evitar problemas
        # en URLs y búsquedas).
        return len(usuario) >= 3 and ' ' not in usuario

    # ── Métodos públicos ───────────────────────────────────────────────────

    def registrar(self, usuario: str, email: str,
                    password: str, confirmar: str) -> dict:
        # ══════════════════════════════════════════════════════════
        #  MÉTODO REGISTRAR — Crea una cuenta nueva
        #
        #  Retorna siempre un diccionario: {'ok': bool, 'msg': str}
        #  Este patrón de retorno es consistente en toda la app.
        #  app.py lee resultado['ok'] para saber si funcionó.
        # ══════════════════════════════════════════════════════════

        # ── PASO 1: Limpiar los datos ──────────────────────────────
        # .strip() elimina espacios al inicio y al final del texto.
        # .lower() convierte a minúsculas (emails no distinguen
        # mayúsculas: Roger@gmail.com = roger@gmail.com).
        # Siempre se limpia ANTES de validar para no rechazar
        # datos válidos por un espacio accidental del usuario.
        usuario   = usuario.strip()
        email     = email.strip().lower()
        password  = password.strip()
        confirmar = confirmar.strip()

        # ── PASO 2: Validar los datos ──────────────────────────────
        # El orden importa: del error más obvio al más específico.
        # all([...]) retorna True solo si TODOS los valores son
        # verdaderos (no vacíos). Si alguno está vacío, falla.
        if not all([usuario, email, password, confirmar]):
            return {'ok': False, 'msg': 'Todos los campos son obligatorios'}

        if not self._usuario_valido(usuario):
            return {'ok': False, 'msg': 'El usuario debe tener mínimo 3 caracteres y sin espacios'}

        if not self._email_valido(email):
            return {'ok': False, 'msg': 'El formato del correo no es válido'}

        if not self._password_valida(password):
            return {'ok': False, 'msg': 'La contraseña debe tener mínimo 8 caracteres'}

        if password != confirmar:
            return {'ok': False, 'msg': 'Las contraseñas no coinciden'}

        # ── PASO 3: Verificar en BD y guardar ─────────────────────
        try:
            cur = self.mysql.connection.cursor()

            # Primero revisamos si el email o usuario ya existen.
            # Usamos OR para verificar ambos en una sola query.
            # Si fetchone() retorna algo, ya existe un registro.
            cur.execute(
                'SELECT id FROM usuarios WHERE email = %s OR usuario = %s',
                (email, usuario)
            )
            if cur.fetchone():
                cur.close()
                return {'ok': False, 'msg': 'El usuario o correo ya está registrado'}

            # SEGURIDAD — Hashear la contraseña antes de guardarla.
            # generate_password_hash transforma "miPassword123"
            # en algo como "pbkdf2:sha256:600000$abc...xyz".
            # Este proceso es IRREVERSIBLE — nadie puede obtener
            # la contraseña original a partir del hash.
            hash_pw = generate_password_hash(password)

            cur.execute(
                'INSERT INTO usuarios (usuario, email, password) VALUES (%s, %s, %s)',
                (usuario, email, hash_pw)
            )

            # commit() confirma los cambios en la BD.
            # Sin commit(), el INSERT se cancela al cerrar la conexión.
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': '¡Cuenta creada! Ya puedes iniciar sesión'}

        except Exception as e:
            # Si algo falla (BD caída, error SQL, etc.), capturamos
            # la excepción y retornamos el error sin romper la app.
            return {'ok': False, 'msg': f'Error en la base de datos: {str(e)}'}

    def autenticar(self, email: str, password: str) -> dict:
        # ══════════════════════════════════════════════════════════
        #  MÉTODO AUTENTICAR — Verifica credenciales al hacer login
        #
        #  Retorna el mismo patrón: {'ok': bool, ...}
        #  Si ok=True, también retorna id, usuario y rol
        #  para que app.py los guarde en la sesión.
        # ══════════════════════════════════════════════════════════

        # Limpiar antes de usar (misma razón que en registrar)
        email    = email.strip().lower()
        password = password.strip()

        if not email or not password:
            return {'ok': False, 'msg': 'Ingresa tu correo y contraseña'}

        try:
            cur = self.mysql.connection.cursor()

            # Buscamos al usuario por su email.
            # Traemos también el hash de contraseña y el rol.
            cur.execute(
                'SELECT id, usuario, password, rol FROM usuarios WHERE email = %s',
                (email,)
            )
            row = cur.fetchone()
            cur.close()

            if not row:
                # SEGURIDAD — Mismo mensaje si el email no existe
                # Y si la contraseña es incorrecta. Así un atacante
                # no puede saber qué emails están registrados
                # probando distintos correos.
                return {'ok': False, 'msg': 'Correo o contraseña incorrectos'}

            # ── Compatibilidad de cursor ───────────────────────────
            # Según la configuración de MySQL, las filas pueden
            # venir como DICCIONARIO {'id': 1, 'usuario': 'Roger'}
            # o como TUPLA (1, 'Roger', 'hash', 'usuario').
            # Este bloque maneja ambos casos para que el código
            # funcione sin importar cómo esté configurada la BD.
            if isinstance(row, dict):
                uid     = row['id']
                usuario = row['usuario']
                pw_hash = row['password']
                rol     = row.get('rol', 'usuario')
            else:
                uid     = row[0]
                usuario = row[1]
                pw_hash = row[2]
                rol     = row[3] if len(row) > 3 else 'usuario'

            # ── Verificación de contraseña ─────────────────────────
            # check_password_hash compara la contraseña que escribió
            # el usuario con el hash guardado en la BD.
            # No "desencripta" — vuelve a hashear y compara.
            # Si coinciden, las credenciales son correctas.
            if check_password_hash(pw_hash, password):
                return {'ok': True, 'id': uid, 'usuario': usuario, 'rol': rol}

            # Mismo mensaje que cuando el email no existe (por seguridad)
            return {'ok': False, 'msg': 'Correo o contraseña incorrectos'}

        except Exception as e:
            return {'ok': False, 'msg': f'Error en la base de datos: {str(e)}'}