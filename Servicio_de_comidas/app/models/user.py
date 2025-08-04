# models/user.py
from sqlalchemy import Column, String, Text
from app.models.base_model import BaseModel
from app.extensions import db  # o desde tu archivo db.py

class User(BaseModel, db.Model):
    __tablename__ = 'user'

    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    preferences = Column(Text, nullable=True)
