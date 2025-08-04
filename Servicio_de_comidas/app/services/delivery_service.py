# services/delivery_service.py
from sqlalchemy.orm import Session
from app.models.subscription import ScheduledMeal
from app.models.dish import Dish
from app.models.user import User
from collections import defaultdict

class DeliveryService:
    def __init__(self, session: Session):
        self.session = session

    def get_deliveries_for_date(self, delivery_date):
        """Devuelve un resumen: qué comidas entregar a cada usuario"""
        meals = self.session.query(ScheduledMeal).filter_by(date=delivery_date).all()
        user_map = defaultdict(list)

        for meal in meals:
            if not meal.dish_id:
                continue
            dish = self.session.get(Dish, meal.dish_id)
            user_sub = self.session.get(meal.__class__.user_subscription.property.mapper.class_, meal.user_subscription_id)
            user = self.session.get(User, user_sub.user_id)
            user_map[user.id].append({
                "name": user.name,
                "address": user.address,
                "meal_type": meal.meal_type,
                "dish": {
                    "name": dish.name,
                    "description": dish.description
                }
            })

        return user_map
