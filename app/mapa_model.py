class PuntosAcopio:
    """Gestiona los puntos de acopio de reciclaje en Bogotá."""

    PUNTOS = [
        {
            'nombre':    'EcoPlanta Chapinero',
            'tipo':      'reciclaje',
            'emoji':     '♻️',
            'direccion': 'Cra 7 #45-12, Chapinero',
            'materiales':'Plástico, Papel, Vidrio',
            'lat':       4.6282,
            'lng':      -74.0641,
            'abierto':   True
        },
        {
            'nombre':    'Centro Reciclaje Norte',
            'tipo':      'centro',
            'emoji':     '🏭',
            'direccion': 'Av 19 #120-45, Usaquén',
            'materiales':'Metal, Plástico, Cartón',
            'lat':       4.7109,
            'lng':      -74.0318,
            'abierto':   True
        },
        {
            'nombre':    'Punto Limpio Usaquén',
            'tipo':      'reciclaje',
            'emoji':     '🗑️',
            'direccion': 'Cll 127 #15-30, Usaquén',
            'materiales':'Todos los materiales',
            'lat':       4.7040,
            'lng':      -74.0316,
            'abierto':   False
        },
        {
            'nombre':    'ReciclaYa Suba',
            'tipo':      'empresa',
            'emoji':     '🏢',
            'direccion': 'Cra 91 #145-20, Suba',
            'materiales':'Plástico, Metal, Vidrio',
            'lat':       4.7418,
            'lng':      -74.0927,
            'abierto':   True
        },
        {
            'nombre':    'EcoVerde Teusaquillo',
            'tipo':      'reciclaje',
            'emoji':     '♻️',
            'direccion': 'Cll 45 #24-10, Teusaquillo',
            'materiales':'Papel, Cartón, Plástico',
            'lat':       4.6418,
            'lng':      -74.0836,
            'abierto':   True
        },
        {
            'nombre':    'Centro Ambiental Kennedy',
            'tipo':      'centro',
            'emoji':     '🏭',
            'direccion': 'Av Américas #68-40, Kennedy',
            'materiales':'Todos los materiales',
            'lat':       4.6282,
            'lng':      -74.1336,
            'abierto':   True
        },
        {
            'nombre':    'ReciclaCol Fontibón',
            'tipo':      'empresa',
            'emoji':     '🏢',
            'direccion': 'Cra 99 #23-15, Fontibón',
            'materiales':'Metal, Cobre, Aluminio',
            'lat':       4.6718,
            'lng':      -74.1427,
            'abierto':   False
        },
        {
            'nombre':    'Punto Verde Bosa',
            'tipo':      'reciclaje',
            'emoji':     '♻️',
            'direccion': 'Cll 65 Sur #80-12, Bosa',
            'materiales':'Plástico, Papel, Vidrio',
            'lat':       4.6109,
            'lng':      -74.1836,
            'abierto':   True
        },
        {
            'nombre':    'EcoMetal Puente Aranda',
            'tipo':      'empresa',
            'emoji':     '🏢',
            'direccion': 'Cra 53 #14-28, Puente Aranda',
            'materiales':'Metal, Chatarra, Cobre',
            'lat':       4.6218,
            'lng':      -74.1036,
            'abierto':   True
        },
        {
            'nombre':    'Recicladora San Cristóbal',
            'tipo':      'reciclaje',
            'emoji':     '♻️',
            'direccion': 'Cll 22 Sur #5-40, San Cristóbal',
            'materiales':'Papel, Cartón, Vidrio',
            'lat':       4.5718,
            'lng':      -74.0836,
            'abierto':   True
        },
    ]

    def obtener_todos(self) -> list:
        """Retorna todos los puntos de acopio."""
        return self.PUNTOS

    def obtener_por_tipo(self, tipo: str) -> list:
        """Filtra puntos por tipo."""
        return [p for p in self.PUNTOS if p['tipo'] == tipo]