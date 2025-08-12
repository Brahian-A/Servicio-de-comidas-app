# app/services/subscription_service.py
from datetime import date, timedelta
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from app.models.subscription import SubscriptionPlan, UserSubscription, ScheduledMeal

class SubscriptionService:
    def __init__(self, session):
        self.session = session

    def _normalize_name(self, name: str) -> str:
        return " ".join(name.strip().split()).lower()

    def _validate_plan(self, *, meals_per_day: int, days_per_week: int, deliveries_per_week: int, price: float):
        if meals_per_day < 1:
            raise ValueError("meals_per_day must be >= 1")
        if not (1 <= days_per_week <= 7):
            raise ValueError("days_per_week must be between 1 and 7")
        if not (1 <= deliveries_per_week <= 7):
            raise ValueError("deliveries_per_week must be between 1 and 7")
        if deliveries_per_week > days_per_week:
            raise ValueError("deliveries_per_week must be <= days_per_week")
        if price is None or price <= 0:
            raise ValueError("price must be > 0")

    # --- PLANES ---
    def create_plan(self, **data) -> SubscriptionPlan:
        # validar
        self._validate_plan(
            meals_per_day=data["meals_per_day"],
            days_per_week=data["days_per_week"],
            deliveries_per_week=data["deliveries_per_week"],
            price=data["price"],
        )
        # conservar name “humano” y guardar normalizado aparte
        data["normalized_name"] = self._normalize_name(data["name"])

        plan = SubscriptionPlan(**data)
        try:
            self.session.add(plan)
            self.session.commit()
            return plan
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Plan name already exists")

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

        # calcular valores resultantes para validar
        meals = data.get("meals_per_day", plan.meals_per_day)
        days = data.get("days_per_week", plan.days_per_week)
        deliv = data.get("deliveries_per_week", plan.deliveries_per_week)
        price = data.get("price", plan.price)
        self._validate_plan(meals_per_day=meals, days_per_week=days, deliveries_per_week=deliv, price=price)

        # actualizar nombre (humano + normalizado)
        if "name" in data and data["name"]:
            plan.name = data["name"]
            plan.normalized_name = self._normalize_name(data["name"])

        # actualizar demás campos
        for k in ("meals_per_day", "days_per_week", "deliveries_per_week", "price"):
            if k in data and data[k] is not None:
                setattr(plan, k, data[k])

        try:
            self.session.commit()
            return plan
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Plan name already exists")

    def delete_plan(self, plan_id: str) -> None:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")
        any_sub = (
            self.session.query(UserSubscription)
            .filter_by(plan_id=plan_id)
            .first()
        )
        if any_sub:
            raise ValueError("Plan is referenced by subscriptions")
        self.session.delete(plan)
        self.session.commit()


    # --- SUSCRIPCIONES ---
    def assign_plan_to_user(self, user_id: str, plan_id: str, start_date: date, weeks: int = 4) -> UserSubscription:
        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError("Plan not found")

        end_date = start_date + timedelta(weeks=weeks)

        # Evitar DOS suscripciones activas solapadas para el mismo usuario
        overlapping = (
            self.session.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id,
                UserSubscription.is_active.is_(True),
                # solape: existing.start <= new.end AND existing.end >= new.start
                and_(UserSubscription.start_date <= end_date, UserSubscription.end_date >= start_date)
            )
            .first()
        )
        if overlapping:
            raise ValueError("User already has an active subscription in that period")

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

        # Generación simple de meals
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
        if not sub:
            raise ValueError("Subscription not found")

        today = date.today()

        # Si estaba pausada y activa → reanudar normal
        if sub.is_active and sub.is_paused:
            sub.is_paused = False
            self.session.commit()
            return sub

        # Si estaba cancelada (is_active=False) PERO no venció y tiene comidas → reactivar
        if (not sub.is_active) and (sub.end_date >= today) and (sub.meals_remaining > 0):
            sub.is_active = True
            sub.is_paused = False
            self.session.commit()
            return sub

        raise ValueError("Subscription cannot be resumed (expired or no meals left)")

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
            slots = [0, 3, 5, 2, 4, 6, 1]
            for day_idx in slots[:deliveries_per_week]:
                results.append((week_start + timedelta(days=day_idx)).isoformat())
        return results
