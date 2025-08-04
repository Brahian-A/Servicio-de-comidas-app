# repositories/user_repository.py
from app.repositories.base import SQLAlchemyRepository
from app.models.user import User

class UserRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(User, session)
