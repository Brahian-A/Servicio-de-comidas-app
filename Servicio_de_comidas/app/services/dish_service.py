# services/dish_service.py
from datetime import date
from app.repositories.dish_repository import DishRepository
from app.models.dish import Dish

class DishService:
    def __init__(self, session):
        self.repo = DishRepository(session)

    def create_dish(self, name, type, description, price, available_on_date):
        existing = self.repo.get_by_name_and_date(name, available_on_date)
        if existing:
            raise ValueError(f"El plato '{name}' ya existe para el día {available_on_date}")

        return self.repo.create(
            name=name,
            type=type,
            description=description,
            price=price,
            available_on_date=available_on_date,
            is_active=True
        )

    def get_available_dishes_for_tomorrow(self):
        tomorrow = date.today().replace(day=date.today().day + 1)
        return self.repo.get_available_for_date(tomorrow)

    def deactivate_dish(self, dish_id):
        dish = self.repo.get(dish_id)
        if dish:
            dish.is_active = False
            self.repo.session.commit()
        return dish
