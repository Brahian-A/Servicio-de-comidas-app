# services/scheduled_meal_service.py
from app.repositories.subscription_repository import ScheduledMealRepository
from app.models.dish import Dish
from datetime import date, timedelta

class ScheduledMealService:
    def __init__(self, session):
        self.session = session
        self.repo = ScheduledMealRepository(session)

    def get_weekly_schedule(self, user_subscription_id, start_date=None):
        if not start_date:
            start_date = date.today()
        end_date = start_date + timedelta(days=6)

        meals = self.session.query(self.repo.model).filter(
            self.repo.model.user_subscription_id == user_subscription_id,
            self.repo.model.date >= start_date,
            self.repo.model.date <= end_date
        ).all()

        schedule = {}
        for meal in meals:
            key = meal.date.isoformat()
            if key not in schedule:
                schedule[key] = []
            schedule[key].append({
                "meal_type": meal.meal_type,
                "dish_id": meal.dish_id,
                "scheduled_meal_id": meal.id
            })
        return schedule

    def change_dish(self, scheduled_meal_id, dish_id):
        meal = self.repo.get(scheduled_meal_id)
        dish = self.session.get(Dish, dish_id)
        if not meal or not dish:
            return None
        meal.dish_id = dish.id
        self.session.commit()
        return meal

    def get_all_meals_for_date(self, delivery_date):
        """Para cocina: obtener todas las comidas programadas de ese día"""
        return self.session.query(self.repo.model).filter_by(date=delivery_date).all()
