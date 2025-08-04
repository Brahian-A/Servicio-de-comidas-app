# app/models/base_model.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declared_attr

class BaseModel:
    @declared_attr
    def id(cls):
        return Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
