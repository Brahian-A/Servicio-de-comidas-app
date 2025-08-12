"""
in this module we init the app package
"""
from flask import Flask, render_template
from flask_restx import Api
from flask_cors import CORS
from app.extensions import bcrypt, jwt, db

from app.api.v1.dishes import api as dishes_ns
from app.api.v1.orders import api as orders_ns
from app.api.v1.subscriptions import subscription_ns as subscriptions_ns
from app.api.v1.kitchen import api as kitchen_ns
from app.api.v1.admin import api as admin_ns
from app.api.v1.users import api as users_ns


def create_app(config_class):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)
    app.config['JWT_SECRET_KEY'] = 'mi-clave-supersecreta'

    # Inicialización de extensiones
    jwt.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    from app.services.facade import AppFacade

    with app.app_context():
        app.facade = AppFacade(db.session)
        # Ruta pagina principal

    @app.route('/')
    def index():
        "sirve la pagina principal index.html"
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        """Sirve la página de inicio de sesión (login.html)."""
        return render_template('login.html')
    
    @app.route('/places')
    def place_page():
        """Sirve la página de detalles del lugar (place.html)."""
        return render_template('place.html')

    # API RESTX
    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/docs/')

    # Rutas
    api.add_namespace(dishes_ns, path='/api/v1/dishes')
    api.add_namespace(orders_ns, path='/api/v1/orders')
    api.add_namespace(subscriptions_ns, path='/api/v1/subscriptions')
    api.add_namespace(kitchen_ns, path='/api/v1/kitchen')
    api.add_namespace(admin_ns, path='/api/v1/admin')
    api.add_namespace(users_ns, path='/api/v1/users')


    return app
