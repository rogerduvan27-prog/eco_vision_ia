from datetime import datetime


EMOJIS = {
    'Plástico': '♻️',
    'Metal':    '🥫',
    'Papel':    '📄',
    'Vidrio':   '🍾',
    'Orgánico': '🍌',
    'General':  '❓',
}


class Historial:
    """Gestiona el historial de clasificaciones del usuario."""

    def __init__(self, mysql):
        self.mysql = mysql

    def _formatear_fecha(self, fecha) -> str:
        """Formatea la fecha para mostrar en la UI."""
        if not fecha:
            return '—'
        hoy  = datetime.now().date()
        ayer = datetime.now().date()
        if hasattr(fecha, 'date'):
            d = fecha.date()
        else:
            d = fecha
        if d == hoy:
            return f"Hoy {fecha.strftime('%I:%M %p') if hasattr(fecha,'strftime') else ''}"
        diff = (hoy - d).days
        if diff == 1:
            return 'Ayer'
        if diff < 7:
            return f"Hace {diff} días"
        return fecha.strftime('%d %b %Y') if hasattr(fecha, 'strftime') else str(fecha)

    def obtener_registros(self, usuario_id: int) -> list:
        """Obtiene todos los registros del historial del usuario."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT id, tipo_material, nombre_objeto,
                        confianza, reciclable, peso_kg, fecha
                FROM historial
                WHERE usuario_id = %s
                ORDER BY fecha DESC
            ''', (usuario_id,))
            rows = cur.fetchall()
            cur.close()

            registros = []
            for row in rows:
                if isinstance(row, dict):
                    tipo = row['tipo_material']
                    registros.append({
                        'id':           row['id'],
                        'tipo_material':tipo,
                        'nombre_objeto':row['nombre_objeto'],
                        'confianza':    round(float(row['confianza']), 1),
                        'reciclable':   bool(row['reciclable']),
                        'peso_kg':      float(row['peso_kg']),
                        'fecha_fmt':    self._formatear_fecha(row['fecha']),
                        'emoji':        EMOJIS.get(tipo, '❓'),
                    })
                else:
                    tipo = row[1]
                    registros.append({
                        'id':           row[0],
                        'tipo_material':tipo,
                        'nombre_objeto':row[2],
                        'confianza':    round(float(row[3]), 1),
                        'reciclable':   bool(row[4]),
                        'peso_kg':      float(row[5]),
                        'fecha_fmt':    self._formatear_fecha(row[6]),
                        'emoji':        EMOJIS.get(tipo, '❓'),
                    })
            return registros
        except Exception as e:
            print(f"Error historial: {e}")
            return []

    def obtener_stats(self, usuario_id: int) -> dict:
        """Calcula las estadísticas del historial."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT
                    COUNT(*)                        AS total,
                    SUM(reciclable)                 AS reciclables,
                    ROUND(SUM(peso_kg), 1)          AS kg
                FROM historial
                WHERE usuario_id = %s
            ''', (usuario_id,))
            row = cur.fetchone()
            cur.close()
            if isinstance(row, dict):
                return {
                    'total':      int(row['total'] or 0),
                    'reciclables':int(row['reciclables'] or 0),
                    'kg':         float(row['kg'] or 0),
                }
            return {
                'total':      int(row[0] or 0),
                'reciclables':int(row[1] or 0),
                'kg':         float(row[2] or 0),
            }
        except Exception as e:
            print(f"Error stats historial: {e}")
            return {'total': 0, 'reciclables': 0, 'kg': 0}