from flask_mysqldb import MySQL


class conexion_DB:

    def __init__(self, app=None):
        self.conexion = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.config['MYSQL_HOST']        = 'localhost'
        app.config['MYSQL_USER']        = 'root'
        app.config['MYSQL_PASSWORD']    = ''
        app.config['MYSQL_DB']          = 'ecovision_db'
        app.config['MYSQL_PORT']        = 3306
        app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
        self.conexion = MySQL(app)