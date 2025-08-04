from flask import Flask
from flask_restx import Api

from app.api.v1.users import api as users_ns
from app.api.v1.orders import api as orders_ns
from app.api.v1.dishes import api as dishes_ns
# from app.api.v1.reviews import api as reviews_ns  # si ya no se usa, eliminá esta línea

def create_app():
    app = Flask(__name__)
    api = Api(app, version='1.0', title='Servicio de Comidas API', description='API para gestión de pedidos y suscripciones')

    # Namespaces
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(orders_ns, path='/api/v1/orders')
    api.add_namespace(dishes_ns, path='/api/v1/dishes')
    # api.add_namespace(reviews_ns, path='/api/v1/reviews')  # si no aplica, no lo incluyas

    return app
