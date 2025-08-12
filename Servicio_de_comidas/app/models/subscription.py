from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from app.extensions import db
from datetime import date, timedelta

class SubscriptionPlan(BaseModel, db.Model):
    __tablename__ = 'subscription_plan'
    __table_args__ = (UniqueConstraint('name', name='uq_subscription_plan_name'),)

    name = Column(String(100), nullable=False)
    meals_per_day = Column(Integer, default=1, nullable=False)
    days_per_week = Column(Integer, default=5, nullable=False)
    deliveries_per_week = Column(Integer, default=2, nullable=False)
    price = Column(Float, nullable=False)

    def meals_per_week(self) -> int:
        return (self.meals_per_day or 0) * (self.days_per_week or 0)


class UserSubscription(BaseModel, db.Model):  # <-- faltaba db.Model
    __tablename__ = 'user_subscription'

    user_id = Column(String, ForeignKey('user.id'), nullable=False, index=True)
    plan_id = Column(String, ForeignKey('subscription_plan.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    meals_remaining = Column(Integer, default=0, nullable=False)
    next_delivery_dates = Column(JSON, nullable=True)  # lista de fechas ISO
    is_active = Column(Boolean, default=True, nullable=False)
    is_paused = Column(Boolean, default=False, nullable=False)

    plan = relationship('SubscriptionPlan')
    scheduled_meals = relationship('ScheduledMeal', back_populates='subscription', cascade='all, delete-orphan')


class ScheduledMeal(BaseModel, db.Model):
    __tablename__ = 'scheduled_meal'

    user_subscription_id = Column(String, ForeignKey('user_subscription.id'), nullable=False, index=True)
    scheduled_for = Column(Date, nullable=False)  # fecha programada
    consumed = Column(Boolean, default=False, nullable=False)

    subscription = relationship('UserSubscription', back_populates='scheduled_meals')
