from datetime import datetime, timedelta


class GraficasDashboard:
    """Provee los datos para las gráficas del dashboard."""

    DIAS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    COLORES = {
        'Plástico': '#52b788',
        'Metal':    '#EF9F27',
        'Vidrio':   '#378ADD',
        'Papel':    '#95d5b2',
        'Orgánico': '#f4845f',
        'General':  '#7aaa8f',
    }

    def __init__(self, mysql):
        self.mysql = mysql

    def actividad_semanal(self, usuario_id: int) -> dict:
        """Clasificaciones por día en los últimos 7 días."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT
                    DAYOFWEEK(fecha) AS dia_num,
                    DAYNAME(fecha)   AS dia_nombre,
                    COUNT(*)         AS total
                FROM historial
                WHERE usuario_id = %s
                    AND fecha >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DAYOFWEEK(fecha), DAYNAME(fecha)
                ORDER BY DAYOFWEEK(fecha)
            ''', (usuario_id,))
            rows = cur.fetchall()
            cur.close()

            # Inicializar 7 días en 0
            datos = {d: 0 for d in self.DIAS}

            mapa_dias = {
                'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mié',
                'Thursday': 'Jue', 'Friday': 'Vie',
                'Saturday': 'Sáb', 'Sunday': 'Dom'
            }

            for row in rows:
                nombre = row['dia_nombre'] if isinstance(row, dict) else row[1]
                total  = row['total']      if isinstance(row, dict) else row[2]
                dia    = mapa_dias.get(nombre, '')
                if dia in datos:
                    datos[dia] = int(total)

            return {
                'labels': list(datos.keys()),
                'data':   list(datos.values()),
                'color':  '#52b788'
            }
        except Exception as e:
            print(f"Error actividad semanal: {e}")
            return {
                'labels': self.DIAS,
                'data':   [0, 0, 0, 0, 0, 0, 0],
                'color':  '#52b788'
            }

    def materiales_distribucion(self, usuario_id: int) -> dict:
        """Distribución porcentual de materiales clasificados."""
        try:
            cur = self.mysql.connection.cursor()
            cur.execute('''
                SELECT tipo_material, COUNT(*) AS total
                FROM historial
                WHERE usuario_id = %s
                GROUP BY tipo_material
                ORDER BY total DESC
            ''', (usuario_id,))
            rows = cur.fetchall()
            cur.close()

            if not rows:
                return {'labels': [], 'data': [], 'colores': []}

            labels  = []
            data    = []
            colores = []

            for row in rows:
                tipo  = row['tipo_material'] if isinstance(row, dict) else row[0]
                total = row['total']         if isinstance(row, dict) else row[1]
                labels.append(tipo)
                data.append(int(total))
                colores.append(self.COLORES.get(tipo, '#7aaa8f'))

            return {'labels': labels, 'data': data, 'colores': colores}

        except Exception as e:
            print(f"Error distribución materiales: {e}")
            return {'labels': [], 'data': [], 'colores': []}