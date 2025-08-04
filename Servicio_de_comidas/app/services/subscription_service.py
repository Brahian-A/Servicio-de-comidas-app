# services/subscription_service.py
from datetime import timedelta, date
from app.models.subscription import SubscriptionPlan, UserSubscription, ScheduledMeal
from app.repositories.subscription_repository import (
    SubscriptionPlanRepository,
    UserSubscriptionRepository,
    ScheduledMealRepository,
)
from app.models.dish import Dish

class SubscriptionService:
    def __init__(self, session):
        self.session = session
        self.plan_repo = SubscriptionPlanRepository(session)
        self.user_sub_repo = UserSubscriptionRepository(session)
        self.scheduled_repo = ScheduledMealRepository(session)

    # ------------------------------
    # Planes
    # ------------------------------
    def create_plan(self, name, meals_per_day, days_per_week, deliveries_per_week, price):
        return self.plan_repo.create(
            name=name,
            meals_per_day=meals_per_day,
            days_per_week=days_per_week,
            deliveries_per_week=deliveries_per_week,
            price=price
        )

    def get_all_plans(self):
        return self.plan_repo.get_all()

    # ------------------------------
    # Suscripciones de usuario
    # ------------------------------
    def subscribe_user(self, user_id, plan_id, start_date, duration_weeks=4):
        plan = self.plan_repo.get(plan_id)
        end_date = start_date + timedelta(weeks=duration_weeks)
        meals_total = plan.meals_per_day * plan.days_per_week * duration_weeks

        sub = self.user_sub_repo.create(
            user_id=user_id,
            plan_id=plan.id,
            start_date=start_date,
            end_date=end_date,
            meals_remaining=meals_total,
            next_delivery_dates=[]
        )

        self.generate_scheduled_meals(sub, plan, start_date, end_date)
        return sub

    # ------------------------------
    # Generación de comidas
    # ------------------------------
    def generate_scheduled_meals(self, subscription, plan, start_date, end_date):
        current = start_date
        days = 0
        while current <= end_date and days < plan.days_per_week * 4:
            for meal_type in ["desayuno", "almuerzo", "cena"][:plan.meals_per_day]:
                self.scheduled_repo.create(
                    user_subscription_id=subscription.id,
                    date=current,
                    meal_type=meal_type,
                    dish_id=None  # luego el usuario puede elegir
                )
            current += timedelta(days=1)
            days += 1
        self.session.commit()

    def get_user_meals_for_date(self, user_subscription_id, date_):
        return self.scheduled_repo.get_meals_for_date(user_subscription_id, date_)

    def assign_dish_to_meal(self, scheduled_meal_id, dish_id):
        meal = self.scheduled_repo.get(scheduled_meal_id)
        dish = self.session.get(Dish, dish_id)
        if meal and dish:
            meal.dish_id = dish.id
            self.session.commit()
            return meal
        return None
