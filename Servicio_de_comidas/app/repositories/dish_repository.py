# repositories/dish_repository.py
from app.repositories.base import SQLAlchemyRepository
from app.models.dish import Dish

class DishRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(Dish, session)

    def get_available_for_date(self, date):
        return self.session.query(self.model).filter_by(available_on_date=date, is_active=True).all()
