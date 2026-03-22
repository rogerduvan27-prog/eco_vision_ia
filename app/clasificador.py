class ClasificadorResiduos:
    """
    Clase principal de clasificación de residuos.
    Mapea las predicciones de MobileNet a categorías de reciclaje.
    """

    # Mapeo de clases ImageNet → categoría de residuo
    CATEGORIAS = {
        # Plástico
        'bottle':           {'tipo': 'Plástico',  'nombre': 'Botella PET',      'emoji': '♻️',  'reciclable': True,  'contenedor': 'Azul',   'precio': 400,  'color': 'green'},
        'water_bottle':     {'tipo': 'Plástico',  'nombre': 'Botella de agua',  'emoji': '💧',  'reciclable': True,  'contenedor': 'Azul',   'precio': 400,  'color': 'green'},
        'pop_bottle':       {'tipo': 'Plástico',  'nombre': 'Botella plástica', 'emoji': '🥤',  'reciclable': True,  'contenedor': 'Azul',   'precio': 350,  'color': 'green'},
        'plastic_bag':      {'tipo': 'Plástico',  'nombre': 'Bolsa plástica',   'emoji': '🛍️', 'reciclable': False, 'contenedor': 'Negro',  'precio': 0,    'color': 'red'},
        # Papel y cartón
        'newspaper':        {'tipo': 'Papel',     'nombre': 'Periódico',        'emoji': '📰',  'reciclable': True,  'contenedor': 'Gris',   'precio': 100,  'color': 'amber'},
        'book':             {'tipo': 'Papel',     'nombre': 'Papel / Libro',    'emoji': '📄',  'reciclable': True,  'contenedor': 'Gris',   'precio': 200,  'color': 'amber'},
        'envelope':         {'tipo': 'Papel',     'nombre': 'Cartón',           'emoji': '📦',  'reciclable': True,  'contenedor': 'Gris',   'precio': 120,  'color': 'amber'},
        'carton':           {'tipo': 'Papel',     'nombre': 'Cartón',           'emoji': '📦',  'reciclable': True,  'contenedor': 'Gris',   'precio': 120,  'color': 'amber'},
        # Vidrio
        'wine_bottle':      {'tipo': 'Vidrio',    'nombre': 'Botella de vidrio','emoji': '🍾',  'reciclable': True,  'contenedor': 'Verde',  'precio': 180,  'color': 'blue'},
        'beer_bottle':      {'tipo': 'Vidrio',    'nombre': 'Botella de vidrio','emoji': '🍺',  'reciclable': True,  'contenedor': 'Verde',  'precio': 180,  'color': 'blue'},
        'glass':            {'tipo': 'Vidrio',    'nombre': 'Vidrio',           'emoji': '🥛',  'reciclable': True,  'contenedor': 'Verde',  'precio': 120,  'color': 'blue'},
        # Metal
        'can':              {'tipo': 'Metal',     'nombre': 'Lata de aluminio', 'emoji': '🥫',  'reciclable': True,  'contenedor': 'Gris',   'precio': 2500, 'color': 'amber'},
        'tin_can':          {'tipo': 'Metal',     'nombre': 'Lata metálica',    'emoji': '🥫',  'reciclable': True,  'contenedor': 'Gris',   'precio': 600,  'color': 'amber'},
        'pop_can':          {'tipo': 'Metal',     'nombre': 'Lata de bebida',   'emoji': '🧃',  'reciclable': True,  'contenedor': 'Gris',   'precio': 2500, 'color': 'amber'},
        # Orgánico
        'banana':           {'tipo': 'Orgánico',  'nombre': 'Residuo orgánico', 'emoji': '🍌',  'reciclable': False, 'contenedor': 'Marrón', 'precio': 0,    'color': 'red'},
        'apple':            {'tipo': 'Orgánico',  'nombre': 'Residuo orgánico', 'emoji': '🍎',  'reciclable': False, 'contenedor': 'Marrón', 'precio': 0,    'color': 'red'},
        'orange':           {'tipo': 'Orgánico',  'nombre': 'Residuo orgánico', 'emoji': '🍊',  'reciclable': False, 'contenedor': 'Marrón', 'precio': 0,    'color': 'red'},
    }

    CONSEJOS = {
        'Plástico':  'Enjuaga el envase y retira la tapa antes de depositarlo. El plástico limpio tiene más valor.',
        'Papel':     'Mantén el papel seco y libre de grasa. El papel húmedo no se puede reciclar.',
        'Vidrio':    'Retira tapas metálicas antes de depositarlo. No mezcles vidrio roto sin protección.',
        'Metal':     'Aplasta las latas para ahorrar espacio. El aluminio es uno de los más valiosos.',
        'Orgánico':  'Los residuos orgánicos van al compostaje o contenedor marrón, no al reciclaje.',
        'General':   'Limpia y seca el material antes de reciclarlo para mantener su valor.',
    }

    KEYWORDS = {
        'botella':   'bottle',      'bottle':    'bottle',
        'plastico':  'pop_bottle',  'plastic':   'pop_bottle',
        'papel':     'newspaper',   'paper':     'newspaper',
        'carton':    'envelope',    'cardboard': 'envelope',
        'vidrio':    'wine_bottle', 'glass':     'wine_bottle',
        'lata':      'can',         'can':       'can',
        'aluminio':  'can',         'metal':     'tin_can',
        'organico':  'banana',      'organic':   'banana',
        'periodico': 'newspaper',   'newspaper': 'newspaper',
    }

    def clasificar_por_label(self, label: str, confianza: float) -> dict:
        """Recibe el label de MobileNet y retorna el resultado de clasificación."""
        label_lower = label.lower().replace(' ', '_')

        # Buscar coincidencia directa
        categoria = self.CATEGORIAS.get(label_lower)

        # Buscar por keyword si no hay coincidencia directa
        if not categoria:
            for key, mapped in self.KEYWORDS.items():
                if key in label_lower:
                    categoria = self.CATEGORIAS.get(mapped)
                    break

        # Default si no se reconoce
        if not categoria:
            categoria = {
                'tipo': 'Desconocido', 'nombre': label.replace('_', ' ').title(),
                'emoji': '❓', 'reciclable': False,
                'contenedor': 'Negro', 'precio': 0, 'color': 'red'
            }

        tipo = categoria['tipo']
        return {
            'nombre':      categoria['nombre'],
            'tipo':        tipo,
            'emoji':       categoria['emoji'],
            'reciclable':  categoria['reciclable'],
            'contenedor':  categoria['contenedor'],
            'precio':      categoria['precio'],
            'color':       categoria['color'],
            'confianza':   round(confianza * 100, 1),
            'consejo':     self.CONSEJOS.get(tipo, self.CONSEJOS['General']),
            'label_ia':    label
        }

    def guardar_historial(self, mysql, usuario_id: int, resultado: dict) -> dict:
        """Guarda la clasificación en el historial del usuario."""
        try:
            cur = mysql.connection.cursor()
            cur.execute('''
                INSERT INTO historial
                    (usuario_id, tipo_material, nombre_objeto,
                    confianza, reciclable, peso_kg)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                usuario_id,
                resultado['tipo'],
                resultado['nombre'],
                resultado['confianza'],
                1 if resultado['reciclable'] else 0,
                0.1
            ))
            mysql.connection.commit()
            cur.close()
            return {'ok': True, 'msg': '¡Guardado en tu historial!'}
        except Exception as e:
            return {'ok': False, 'msg': f'Error al guardar: {str(e)}'}