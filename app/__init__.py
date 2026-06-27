from flask import Flask
from flask_mail import Mail
import os

mail = Mail()

_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__,
        template_folder=os.path.join(_root_dir, 'templates'),
        static_folder=os.path.join(_root_dir, 'static'))

    app.secret_key = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_para_desarrollo')

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'verdeqr.app@gmail.com'
    app.config['MAIL_PASSWORD'] = 'clave_de_aplicacion'
    app.config['MAIL_DEFAULT_SENDER'] = 'verdeqr.app@gmail.com'
    app.config['MAIL_SUPPRESS_SEND'] = True

    mail.init_app(app)

    from .db import init_db_config
    init_db_config()

    from .utils import determinar_genero
    app.jinja_env.globals['determinar_genero'] = determinar_genero

    from .auth import auth_bp
    from .admin import admin_bp
    from .arboles import arboles_bp
    from .especies import especies_bp
    from .usos import usos_bp
    from .qr import qr_bp
    from .info import info_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(arboles_bp)
    app.register_blueprint(especies_bp)
    app.register_blueprint(usos_bp)
    app.register_blueprint(qr_bp)
    app.register_blueprint(info_bp)

    from .db import close_db
    app.teardown_appcontext(close_db)

    from .db import get_db_connection
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            print("Conexión a la base de datos establecida correctamente")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {str(e)}")
    finally:
        if 'connection' in locals():
            connection.close()

    return app
