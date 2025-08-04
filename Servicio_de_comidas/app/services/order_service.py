# services/order_service.py
from datetime import date
from app.repositories.order_repository import OrderRepository
from app.models.order import Order, OrderDish
from app.models.dish import Dish

class OrderService:
    def __init__(self, session):
        self.repo = OrderRepository(session)
        self.session = session

    def create_order(self, user_id, dish_items: list):
        """
        dish_items = [
            {'dish_id': 'xxx', 'quantity': 2},
            {'dish_id': 'yyy', 'quantity': 1}
        ]
        """
        order = Order(user_id=user_id, date=date.today(), status='pending', total_price=0.0)
        self.session.add(order)
        self.session.flush()  # para obtener el order.id

        total = 0
        for item in dish_items:
            dish = self.session.get(Dish, item['dish_id'])
            if not dish or not dish.is_active:
                continue
            quantity = item.get('quantity', 1)
            total += dish.price * quantity
            order_dish = OrderDish(order_id=order.id, dish_id=dish.id, quantity=quantity)
            self.session.add(order_dish)

        order.total_price = total
        self.session.commit()
        return order

    def get_orders_by_user(self, user_id):
        return self.repo.get_by_user(user_id)