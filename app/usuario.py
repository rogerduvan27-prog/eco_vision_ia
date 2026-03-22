import re
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:
    """Encapsula toda la lógica de autenticación y registro de usuarios."""

    def __init__(self, mysql):
        self.mysql = mysql

    # ── Validaciones privadas ──────────────────────────────────────────────

    def _email_valido(self, email: str) -> bool:
        return bool(re.match(r'^[\w.\-]+@[\w.\-]+\.\w{2,}$', email))

    def _password_valida(self, password: str) -> bool:
        return len(password) >= 8

    def _usuario_valido(self, usuario: str) -> bool:
        return len(usuario) >= 3 and ' ' not in usuario

    # ── Métodos públicos ───────────────────────────────────────────────────

    def registrar(self, usuario: str, email: str,
                    password: str, confirmar: str) -> dict:
        """Valida y persiste un nuevo usuario en la BD."""

        usuario   = usuario.strip()
        email     = email.strip().lower()
        password  = password.strip()
        confirmar = confirmar.strip()

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

        try:
            cur = self.mysql.connection.cursor()
            cur.execute(
                'SELECT id FROM usuarios WHERE email = %s OR usuario = %s',
                (email, usuario)
            )
            if cur.fetchone():
                cur.close()
                return {'ok': False, 'msg': 'El usuario o correo ya está registrado'}

            hash_pw = generate_password_hash(password)
            cur.execute(
                'INSERT INTO usuarios (usuario, email, password) VALUES (%s, %s, %s)',
                (usuario, email, hash_pw)
            )
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': '¡Cuenta creada! Ya puedes iniciar sesión'}

        except Exception as e:
            return {'ok': False, 'msg': f'Error en la base de datos: {str(e)}'}

    def autenticar(self, email: str, password: str) -> dict:
        """Verifica credenciales y retorna datos del usuario si son correctas."""

        email    = email.strip().lower()
        password = password.strip()

        if not email or not password:
            return {'ok': False, 'msg': 'Ingresa tu correo y contraseña'}

        try:
            cur = self.mysql.connection.cursor()
            cur.execute(
                'SELECT id, usuario, password, rol FROM usuarios WHERE email = %s',
                (email,)
            )
            row = cur.fetchone()
            cur.close()

            if not row:
                return {'ok': False, 'msg': 'Correo o contraseña incorrectos'}

            # Manejar tanto DictCursor como cursor normal
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

            if check_password_hash(pw_hash, password):
                return {'ok': True, 'id': uid, 'usuario': usuario, 'rol': rol}

            return {'ok': False, 'msg': 'Correo o contraseña incorrectos'}

        except Exception as e:
            return {'ok': False, 'msg': f'Error en la base de datos: {str(e)}'}