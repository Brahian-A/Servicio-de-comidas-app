# run.py

from app import create_app
from config import DevelopmentConfig
from app.extensions import db
from app.models.user import User
from app.models.dish import Dish
from app.models.order import Order, OrderDish
from app.models.subscription import SubscriptionPlan, UserSubscription, ScheduledMeal

# Crear la app con la configuración de desarrollo
app = create_app(DevelopmentConfig)

# Crear la base de datos si no existe
with app.app_context():
    db.create_all()

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
