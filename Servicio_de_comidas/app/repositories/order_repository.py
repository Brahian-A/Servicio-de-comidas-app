# repositories/order_repository.py
from app.repositories.base import SQLAlchemyRepository
from app.models.order import Order

class OrderRepository(SQLAlchemyRepository):
    def __init__(self, session):
        super().__init__(Order, session)

    def get_by_user(self, user_id):
        return self.session.query(self.model).filter_by(user_id=user_id).all()
