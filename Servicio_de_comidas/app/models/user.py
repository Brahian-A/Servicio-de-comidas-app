from sqlalchemy import Column, String, Text
from werkzeug.security import generate_password_hash, check_password_hash  # 👈 FALTA ESTO
from app.models.base_model import BaseModel
from app.extensions import db

class User(BaseModel, db.Model):
    __tablename__ = 'user'

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    preferences = Column(Text, nullable=True)
    password_hash = Column(String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'address': self.address,
            'phone': self.phone,
            'preferences': self.preferences,
                }