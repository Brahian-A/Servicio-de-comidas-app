# models/order.py
from sqlalchemy import Column, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
from app.extensions import db

class Order(BaseModel, db.Model):
    __tablename__ = 'orders'

    user_id = Column(String, ForeignKey('user.id'), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, delivered, cancelled
    total_price = Column(Float, default=0.0)

    dishes = relationship('OrderDish', back_populates='order', cascade='all, delete-orphan')


class OrderDish(db.Model):
    __tablename__ = 'order_dish'

    order_id = Column(String, ForeignKey('orders.id'), primary_key=True)
    dish_id = Column(String, ForeignKey('dish.id'), primary_key=True)
    quantity = Column(Float, nullable=False, default=1)

    order = relationship('Order', back_populates='dishes')
    dish = relationship('Dish')