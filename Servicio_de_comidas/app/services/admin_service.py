# services/admin_service.py
from app.models.order import OrderDish
from app.models.subscription import ScheduledMeal
from sqlalchemy import func
from datetime import date

class AdminService:
    def __init__(self, session):
        self.session = session

    def count_dishes_for_day(self, delivery_date):
        """Cantidad de veces que hay que preparar cada plato"""
        result = (
            self.session.query(ScheduledMeal.dish_id, func.count(ScheduledMeal.id))
            .filter(ScheduledMeal.date == delivery_date, ScheduledMeal.dish_id.isnot(None))
            .group_by(ScheduledMeal.dish_id)
            .all()
        )
        return {dish_id: count for dish_id, count in result}

    def most_requested_dishes(self, limit=5):
        return (
            self.session.query(OrderDish.dish_id, func.count(OrderDish.dish_id))
            .group_by(OrderDish.dish_id)
            .order_by(func.count(OrderDish.dish_id).desc())
            .limit(limit)
            .all()
        )
