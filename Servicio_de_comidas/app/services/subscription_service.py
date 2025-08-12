from datetime import date, timedelta
from typing import List, Optional
from app.models.subscription import SubscriptionPlan, UserSubscription, ScheduledMeal

class SubscriptionService:
    def __init__(self, session):
        self.session = session

    # --- PLANES ---
    def create_plan(self, **data) -> SubscriptionPlan:
        plan = SubscriptionPlan(**data)
        self.session.add(plan)
        self.session.commit()
        return plan

    def list_plans(self) -> List[SubscriptionPlan]:
        return (
            self.session.query(SubscriptionPlan)
            .order_by(SubscriptionPlan.name.asc())
            .all()
        )

    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        return self.session.get(SubscriptionPlan, plan_id)

    def update_plan(self, plan_id: str, **data) -> SubscriptionPlan:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        for k, v in data.items():
            setattr(plan, k, v)
        self.session.commit()
        return plan

    def delete_plan(self, plan_id: str) -> None:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        # Evitar borrar si hay suscripciones activas
        active_count = (
            self.session.query(UserSubscription)
            .filter_by(plan_id=plan_id, is_active=True)
            .count()
        )
        if active_count > 0:
            raise ValueError("Plan is in use by active subscriptions")
        self.session.delete(plan)
        self.session.commit()

    # --- SUSCRIPCIONES ---
    def assign_plan_to_user(self, user_id: str, plan_id: str, start_date: date, weeks: int = 4) -> UserSubscription:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        end_date = start_date + timedelta(weeks=weeks)
        total_meals = plan.meals_per_week() * weeks

        subscription = UserSubscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            meals_remaining=total_meals,
            next_delivery_dates=self._compute_delivery_schedule(start_date, weeks, plan.deliveries_per_week),
            is_active=True,
            is_paused=False
        )
        self.session.add(subscription)
        self.session.flush()

        # Pre-generamos ScheduledMeal simples (días corridos)
        current = start_date
        days_needed = plan.days_per_week * weeks
        created = 0
        while created < days_needed:
            for _ in range(plan.meals_per_day):
                self.session.add(ScheduledMeal(user_subscription_id=subscription.id, scheduled_for=current))
            created += 1
            current += timedelta(days=1)

        self.session.commit()
        return subscription

    def list_user_subscriptions(self, user_id: str) -> List[UserSubscription]:
        return (
            self.session.query(UserSubscription)
            .filter_by(user_id=user_id)
            .order_by(UserSubscription.start_date.desc())
            .all()
        )

    def get_subscription(self, subscription_id: str) -> Optional[UserSubscription]:
        return self.session.get(UserSubscription, subscription_id)

    def pause_subscription(self, subscription_id: str) -> UserSubscription:
        sub = self.get_subscription(subscription_id)
        if not sub or not sub.is_active:
            raise ValueError("Subscription not found or inactive")
        sub.is_paused = True
        self.session.commit()
        return sub

    def resume_subscription(self, subscription_id: str) -> UserSubscription:
        sub = self.get_subscription(subscription_id)
        if not sub or not sub.is_active:
            raise ValueError("Subscription not found or inactive")
        sub.is_paused = False
        self.session.commit()
        return sub

    def cancel_subscription(self, subscription_id: str) -> UserSubscription:
        sub = self.get_subscription(subscription_id)
        if not sub:
            raise ValueError("Subscription not found")
        sub.is_active = False
        self.session.commit()
        return sub

    def register_meal_consumption(self, subscription_id: str, target_date: Optional[date] = None) -> UserSubscription:
        sub = self.get_subscription(subscription_id)
        if not sub or not sub.is_active or sub.is_paused:
            raise ValueError("Subscription not found or not consumable")

        if sub.meals_remaining <= 0:
            raise ValueError("No meals remaining")

        q = self.session.query(ScheduledMeal).filter_by(user_subscription_id=sub.id, consumed=False)
        if target_date:
            q = q.filter(ScheduledMeal.scheduled_for == target_date)
        meal = q.order_by(ScheduledMeal.scheduled_for.asc()).first()
        if not meal:
            raise ValueError("No scheduled meal available to consume")

        meal.consumed = True
        sub.meals_remaining -= 1
        self.session.commit()
        return sub

    # --- Helpers ---
    def _compute_delivery_schedule(self, start: date, weeks: int, deliveries_per_week: int) -> list:
        results = []
        base = start
        for w in range(weeks):
            week_start = base + timedelta(weeks=w)
            slots = [0, 3, 5, 2, 4, 6, 1]  # preferencia Lun/Jue/Vie...
            for day_idx in slots[:deliveries_per_week]:
                results.append((week_start + timedelta(days=day_idx)).isoformat())
        return results
