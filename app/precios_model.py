from datetime import datetime


class PreciosMateriales:
    """Gestiona los precios de materiales reciclables en COP."""

    MATERIALES = [
        {
            'nombre':    'Cobre',
            'categoria': 'Metal',
            'emoji':     '🥇',
            'precio_kg': 12000,
            'demanda':   'Alta',
            'color':     'amber'
        },
        {
            'nombre':    'Aluminio',
            'categoria': 'Metal',
            'emoji':     '🔵',
            'precio_kg': 2500,
            'demanda':   'Alta',
            'color':     'blue'
        },
        {
            'nombre':    'Chatarra',
            'categoria': 'Metal',
            'emoji':     '⚙️',
            'precio_kg': 600,
            'demanda':   'Media',
            'color':     'green'
        },
        {
            'nombre':    'Plástico PET',
            'categoria': 'Plástico',
            'emoji':     '♻️',
            'precio_kg': 400,
            'demanda':   'Media',
            'color':     'green'
        },
        {
            'nombre':    'Plástico HDPE',
            'categoria': 'Plástico',
            'emoji':     '🧴',
            'precio_kg': 350,
            'demanda':   'Media',
            'color':     'green'
        },
        {
            'nombre':    'Plástico duro',
            'categoria': 'Plástico',
            'emoji':     '🪣',
            'precio_kg': 200,
            'demanda':   'Baja',
            'color':     'green'
        },
        {
            'nombre':    'Cartón',
            'categoria': 'Papel',
            'emoji':     '📦',
            'precio_kg': 120,
            'demanda':   'Baja',
            'color':     'amber'
        },
        {
            'nombre':    'Papel archivo',
            'categoria': 'Papel',
            'emoji':     '📄',
            'precio_kg': 200,
            'demanda':   'Media',
            'color':     'amber'
        },
        {
            'nombre':    'Periódico',
            'categoria': 'Papel',
            'emoji':     '📰',
            'precio_kg': 100,
            'demanda':   'Baja',
            'color':     'amber'
        },
        {
            'nombre':    'Vidrio transparente',
            'categoria': 'Vidrio',
            'emoji':     '🫙',
            'precio_kg': 180,
            'demanda':   'Media',
            'color':     'green'
        },
        {
            'nombre':    'Vidrio de color',
            'categoria': 'Vidrio',
            'emoji':     '🟢',
            'precio_kg': 120,
            'demanda':   'Baja',
            'color':     'green'
        },
    ]

    def obtener_todos(self) -> list:
        """Retorna todos los materiales ordenados por precio descendente."""
        return sorted(self.MATERIALES, key=lambda x: x['precio_kg'], reverse=True)

    def fecha_hoy(self) -> str:
        """Retorna la fecha actual formateada."""
        meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Ago',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }
        hoy = datetime.now()
        return f"{hoy.day} {meses[hoy.month]} {hoy.year}"