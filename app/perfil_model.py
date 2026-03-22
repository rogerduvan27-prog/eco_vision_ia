import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
UPLOAD_FOLDER      = os.path.join(os.path.dirname(__file__), 'static', 'uploads')


class PerfilUsuario:
    """Encapsula la lógica de actualización del perfil del usuario."""

    def __init__(self, mysql):
        self.mysql = mysql
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    def _extension_valida(self, filename: str) -> bool:
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def obtener(self, usuario_id: int) -> dict:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT id, usuario, email, ciudad, avatar,
                    DATE_FORMAT(creado_en, '%%b %%Y') AS creado_en
                FROM usuarios WHERE id = %s
            ''', (usuario_id,))
            row = cur.fetchone()
            cur.close()
            if row and not isinstance(row, dict):
                return {
                    'id':        row[0],
                    'usuario':   row[1],
                    'email':     row[2],
                    'ciudad':    row[3],
                    'avatar':    row[4],
                    'creado_en': row[5]
                }
            return row or {
                'id': usuario_id, 'usuario': '', 'email': '',
                'ciudad': '', 'avatar': None, 'creado_en': ''
            }
        except Exception as e:
            print(f"Error obtener perfil: {e}")
            return {
                'id': usuario_id, 'usuario': '', 'email': '',
                'ciudad': '', 'avatar': None, 'creado_en': ''
            }

    def actualizar(self, usuario_id: int, ciudad: str,
                password: str, confirmar: str) -> dict:
        ciudad = ciudad.strip()
        if password:
            if len(password) < 8:
                return {'ok': False, 'msg': 'La contraseña debe tener mínimo 8 caracteres'}
            if password != confirmar:
                return {'ok': False, 'msg': 'Las contraseñas no coinciden'}
        try:
            cur = self.mysql.connection.cursor()
            if password:
                hash_pw = generate_password_hash(password)
                cur.execute(
                    'UPDATE usuarios SET ciudad = %s, password = %s WHERE id = %s',
                    (ciudad, hash_pw, usuario_id)
                )
            else:
                cur.execute(
                    'UPDATE usuarios SET ciudad = %s WHERE id = %s',
                    (ciudad, usuario_id)
                )
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': 'Perfil actualizado correctamente'}
        except Exception as e:
            return {'ok': False, 'msg': f'Error al actualizar: {str(e)}'}

    def actualizar_avatar(self, usuario_id: int, archivo) -> dict:
        if not archivo or archivo.filename == '':
            return {'ok': False, 'msg': 'No se seleccionó ninguna imagen'}
        if not self._extension_valida(archivo.filename):
            return {'ok': False, 'msg': 'Formato no válido. Usa JPG, PNG o WEBP'}
        nombre = f"avatar_{usuario_id}_{secure_filename(archivo.filename)}"
        ruta   = os.path.join(UPLOAD_FOLDER, nombre)
        archivo.save(ruta)
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('UPDATE usuarios SET avatar = %s WHERE id = %s',
                        (nombre, usuario_id))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': 'Foto de perfil actualizada'}
        except Exception as e:
            return {'ok': False, 'msg': f'Error al guardar imagen: {str(e)}'}