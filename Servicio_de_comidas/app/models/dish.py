# models/dish.py
from sqlalchemy import Column, String, Float, Boolean, Date
from app.models.base_model import BaseModel
from app.extensions import db

class Dish(BaseModel, db.Model):
    __tablename__ = 'dish'

    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # desayuno, almuerzo, cena
    description = Column(String(500))
    price = Column(Float, nullable=False)
    available_on_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
