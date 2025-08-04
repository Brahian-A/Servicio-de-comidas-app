# repositories/subscription_repository.py
from app.repositories.base import SQLAlchemyRepository
from app.models.subscription import SubscriptionPlan, UserSubscription, ScheduledMeal

class SubscriptionPlanRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(SubscriptionPlan, session)


class UserSubscriptionRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(UserSubscription, session)

    def get_active_by_user(self, user_id, current_date):
        return self.session.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.start_date <= current_date,
            self.model.end_date >= current_date
        ).first()


class ScheduledMealRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(ScheduledMeal, session)

    def get_meals_for_date(self, user_subscription_id, date):
        return self.session.query(self.model).filter_by(
            user_subscription_id=user_subscription_id,
            date=date
        ).all()
