from datetime import datetime


class Tickets:
    """Gestiona el sistema de tickets de soporte (Mesa de ayuda ITIL)."""

    TIPOS = [
        'Error en el clasificador',
        'Problema con el mapa',
        'Error al iniciar sesión',
        'Problema con el perfil',
        'Error en precios',
        'Sugerencia de mejora',
        'Otro',
    ]

    ESTADOS = {
        'abierto':    {'label': 'Abierto',     'color': 'error'},
        'en_proceso': {'label': 'En proceso',  'color': 'amber'},
        'resuelto':   {'label': 'Resuelto',    'color': 'green'},
        'cerrado':    {'label': 'Cerrado',     'color': 'muted'},
    }

    PRIORIDADES = {
        'baja':  {'label': 'Baja',  'color': 'green'},
        'media': {'label': 'Media', 'color': 'amber'},
        'alta':  {'label': 'Alta',  'color': 'error'},
    }

    def __init__(self, mysql):
        self.mysql = mysql

    def _formatear_fecha(self, fecha) -> str:
        if not fecha:
            return '—'
        hoy  = datetime.now().date()
        if hasattr(fecha, 'date'):
            d = fecha.date()
        else:
            return str(fecha)
        diff = (hoy - d).days
        if diff == 0:
            return f"Hoy {fecha.strftime('%I:%M %p')}"
        if diff == 1:
            return 'Ayer'
        if diff < 7:
            return f"Hace {diff} días"
        return fecha.strftime('%d %b %Y')

    # ── Crear ticket ───────────────────────────────────────────
    def crear(self, usuario_id: int, tipo: str,
                descripcion: str, prioridad: str) -> dict:
        if not tipo or not descripcion:
            return {'ok': False, 'msg': 'Completa todos los campos'}
        if len(descripcion.strip()) < 10:
            return {'ok': False, 'msg': 'La descripción debe tener al menos 10 caracteres'}
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                INSERT INTO tickets
                    (usuario_id, tipo, descripcion, prioridad, estado)
                VALUES (%s, %s, %s, %s, 'abierto')
            ''', (usuario_id, tipo, descripcion.strip(), prioridad))
            self.mysql.connection.commit()
            ticket_id = cur.lastrowid
            cur.close()
            return {'ok': True, 'msg': f'Ticket #{ticket_id:03d} creado correctamente',
                    'id': ticket_id}
        except Exception as e:
            return {'ok': False, 'msg': f'Error al crear ticket: {str(e)}'}

    # ── Obtener tickets del usuario ────────────────────────────
    def obtener_por_usuario(self, usuario_id: int) -> list:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT id, tipo, descripcion, prioridad, estado, creado_en
                FROM tickets
                WHERE usuario_id = %s
                ORDER BY creado_en DESC
            ''', (usuario_id,))
            rows = cur.fetchall()
            cur.close()
            return self._formatear_rows(rows)
        except Exception as e:
            print(f"Error tickets usuario: {e}")
            return []

    # ── Obtener todos los tickets (admin) ──────────────────────
    def obtener_todos(self) -> list:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT t.id, t.tipo, t.descripcion, t.prioridad,
                        t.estado, t.creado_en, u.usuario
                FROM tickets t
                JOIN usuarios u ON t.usuario_id = u.id
                ORDER BY t.creado_en DESC
            ''')
            rows = cur.fetchall()
            cur.close()
            return self._formatear_rows(rows, con_usuario=True)
        except Exception as e:
            print(f"Error todos los tickets: {e}")
            return []

    # ── Actualizar estado (admin) ──────────────────────────────
    def actualizar_estado(self, ticket_id: int, estado: str) -> dict:
        if estado not in self.ESTADOS:
            return {'ok': False, 'msg': 'Estado inválido'}
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('UPDATE tickets SET estado = %s WHERE id = %s',
                        (estado, ticket_id))
            self.mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': 'Estado actualizado'}
        except Exception as e:
            return {'ok': False, 'msg': str(e)}

    # ── Stats para admin ───────────────────────────────────────
    def obtener_stats(self) -> dict:
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT
                    COUNT(*) AS total,
                    SUM(estado = 'abierto')    AS abiertos,
                    SUM(estado = 'en_proceso') AS en_proceso,
                    SUM(estado = 'resuelto')   AS resueltos
                FROM tickets
            ''')
            row = cur.fetchone()
            cur.close()
            if isinstance(row, dict):
                return {k: int(v or 0) for k, v in row.items()}
            return {
                'total':      int(row[0] or 0),
                'abiertos':   int(row[1] or 0),
                'en_proceso': int(row[2] or 0),
                'resueltos':  int(row[3] or 0),
            }
        except Exception:
            return {'total': 0, 'abiertos': 0, 'en_proceso': 0, 'resueltos': 0}

    # ── Formatear filas ────────────────────────────────────────
    def _formatear_rows(self, rows, con_usuario=False) -> list:
        result = []
        for row in rows:
            if isinstance(row, dict):
                r = dict(row)
            else:
                keys = ['id','tipo','descripcion','prioridad','estado','creado_en']
                if con_usuario:
                    keys.append('usuario')
                r = dict(zip(keys, row))

            r['fecha_fmt']     = self._formatear_fecha(r.get('creado_en'))
            r['estado_label']  = self.ESTADOS.get(r['estado'], {}).get('label', r['estado'])
            r['estado_color']  = self.ESTADOS.get(r['estado'], {}).get('color', 'muted')
            r['prior_label']   = self.PRIORIDADES.get(r['prioridad'], {}).get('label', r['prioridad'])
            r['prior_color']   = self.PRIORIDADES.get(r['prioridad'], {}).get('color', 'muted')
            result.append(r)
        return result