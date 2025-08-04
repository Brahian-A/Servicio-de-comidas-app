# models/subscription.py
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from app.extensions import db

class SubscriptionPlan(BaseModel, db.Model):
    __tablename__ = 'subscription_plan'

    name = Column(String(100), nullable=False)
    meals_per_day = Column(Integer, default=1)
    days_per_week = Column(Integer, default=5)
    deliveries_per_week = Column(Integer, default=2)
    price = Column(Float, nullable=False)


class UserSubscription(BaseModel):
    __tablename__ = 'user_subscription'

    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    plan_id = Column(String, ForeignKey('subscription_plan.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    meals_remaining = Column(Integer, default=0)
    next_delivery_dates = Column(JSON, nullable=True)

    plan = relationship('SubscriptionPlan')


class ScheduledMeal(BaseModel):
    __tablename__ = 'scheduled_meal'

    user_subscription_id = Column(String, ForeignKey('user_subscription.id'), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String(20), nullable=False)  # desayuno, almuerzo, cena
    dish_id = Column(String, ForeignKey('dish.id'), nullable=True)
