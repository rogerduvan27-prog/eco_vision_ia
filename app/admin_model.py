from werkzeug.security import generate_password_hash


class Admin:
    """Gestiona todas las operaciones del panel de administrador."""

    def __init__(self, mysql):
        self.mysql = mysql

    # ── Verificar si es admin ──────────────────────────────────
    def es_admin(self, usuario_id: int) -> bool:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('SELECT rol FROM usuarios WHERE id = %s', (usuario_id,))
            row = cur.fetchone()
            cur.close()
            if isinstance(row, dict):
                return row.get('rol') == 'admin'
            return row[0] == 'admin' if row else False
        except Exception:
            return False

    # ── Crear cuenta admin ─────────────────────────────────────
    def crear_admin(self, usuario: str, email: str, password: str) -> dict:
        try:
            cur  = self.mysql.connection.cursor()
            hash_pw = generate_password_hash(password)
            cur.execute('''
                INSERT INTO usuarios (usuario, email, password, rol)
                VALUES (%s, %s, %s, 'admin')
            ''', (usuario.strip(), email.strip().lower(), hash_pw))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': 'Admin creado correctamente'}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Stats globales ─────────────────────────────────────────
    def obtener_stats_globales(self) -> dict:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT
                    (SELECT COUNT(*) FROM usuarios WHERE rol = 'usuario') AS usuarios,
                    (SELECT COUNT(*) FROM historial)                      AS clasificaciones,
                    (SELECT COUNT(*) FROM tickets WHERE estado = 'abierto') AS tickets_abiertos,
                    (SELECT COUNT(*) FROM tickets)                        AS tickets_total
            ''')
            row = cur.fetchone()
            cur.close()
            if isinstance(row, dict):
                return {k: int(v or 0) for k, v in row.items()}
            return {
                'usuarios':         int(row[0] or 0),
                'clasificaciones':  int(row[1] or 0),
                'tickets_abiertos': int(row[2] or 0),
                'tickets_total':    int(row[3] or 0),
            }
        except Exception as e:
            print(f"Error stats globales: {e}")
            return {'usuarios': 0, 'clasificaciones': 0,
                    'tickets_abiertos': 0, 'tickets_total': 0}

    # ── Obtener todos los usuarios ─────────────────────────────
    def obtener_usuarios(self) -> list:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT u.id, u.usuario, u.email, u.ciudad, u.creado_en,
                        COUNT(h.id) AS clasificaciones
                FROM usuarios u
                LEFT JOIN historial h ON h.usuario_id = u.id
                WHERE u.rol = 'usuario'
                GROUP BY u.id
                ORDER BY u.creado_en DESC
            ''')
            rows = cur.fetchall()
            cur.close()
            result = []
            for row in rows:
                if isinstance(row, dict):
                    r = dict(row)
                else:
                    r = {
                        'id': row[0], 'usuario': row[1], 'email': row[2],
                        'ciudad': row[3], 'creado_en': row[4],
                        'clasificaciones': int(row[5] or 0)
                    }
                r['clasificaciones'] = int(r.get('clasificaciones') or 0)
                result.append(r)
            return result
        except Exception as e:
            print(f"Error usuarios: {e}")
            return []

    # ── Eliminar usuario ───────────────────────────────────────
    def eliminar_usuario(self, usuario_id: int) -> dict:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('DELETE FROM usuarios WHERE id = %s AND rol = %s',
                        (usuario_id, 'usuario'))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': 'Usuario eliminado correctamente'}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Modo mantenimiento ─────────────────────────────────────
    def obtener_mantenimiento(self) -> bool:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT valor FROM configuracion
                WHERE clave = 'mantenimiento'
            ''')
            row = cur.fetchone()
            cur.close()
            if row:
                val = row['valor'] if isinstance(row, dict) else row[0]
                return val == '1'
            return False
        except Exception:
            return False

    def toggle_mantenimiento(self) -> dict:
        try:
            actual = self.obtener_mantenimiento()
            nuevo  = '0' if actual else '1'
            cur    = self.mysql.connection.cursor()
            cur.execute('''
                INSERT INTO configuracion (clave, valor)
                VALUES ('mantenimiento', %s)
                ON DUPLICATE KEY UPDATE valor = %s
            ''', (nuevo, nuevo))
            self.mysql.connection.commit()
            cur.close()
            estado = 'activado' if nuevo == '1' else 'desactivado'
            return {'ok': True, 'msg': f'Modo mantenimiento {estado}',
                    'activo': nuevo == '1'}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}