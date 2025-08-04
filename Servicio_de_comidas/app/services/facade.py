from app.services.user_service import UserService
from app.services.dish_service import DishService
from app.services.order_service import OrderService
from app.services.subscription_service import SubscriptionService
from app.services.scheduled_meal_service import ScheduledMealService
from app.services.delivery_service import DeliveryService
from app.services.admin_service import AdminService

class AppFacade:
    def __init__(self, session):
        self.user_service = UserService(session)
        self.dish_service = DishService(session)
        self.order_service = OrderService(session)
        self.subscription_service = SubscriptionService(session)
        self.scheduled_meal_service = ScheduledMealService(session)
        self.delivery_service = DeliveryService(session)
        self.admin_service = AdminService(session)

    # Users 👇
    def get_user_by_email(self, email):
        return self.user_service.get_by_email(email)

    def create_user(self, **kwargs):
        return self.user_service.create_user(**kwargs)

    def delete_user(self, user_id):
        return self.user_service.delete_user(user_id)

    def get_all_users(self):
        return self.user_service.get_all_users()

    # Dishes
    def create_dish(self, **kwargs):
        return self.dish_service.create_dish(**kwargs)

    def get_dishes_for_tomorrow(self):
        return self.dish_service.get_available_dishes_for_tomorrow()

    # Orders
    def create_order(self, user_id, dish_items):
        return self.order_service.create_order(user_id, dish_items)

    def get_orders_by_user(self, user_id):
        return self.order_service.get_orders_by_user(user_id)

    # Subscriptions
    def create_subscription_plan(self, **kwargs):
        return self.subscription_service.create_plan(**kwargs)

    def subscribe_user(self, user_id, plan_id, start_date):
        return self.subscription_service.subscribe_user(user_id, plan_id, start_date)

    # Scheduled meals
    def get_user_meals_for_week(self, user_subscription_id, start_date=None):
        return self.scheduled_meal_service.get_weekly_schedule(user_subscription_id, start_date)

    def assign_dish_to_meal(self, scheduled_meal_id, dish_id):
        return self.scheduled_meal_service.change_dish(scheduled_meal_id, dish_id)

    # Cocina/entrega
    def get_deliveries_for_date(self, delivery_date):
        return self.delivery_service.get_deliveries_for_date(delivery_date)

    # Admin
    def get_dish_count_for_day(self, day):
        return self.admin_service.count_dishes_for_day(day)

    def get_top_dishes(self):
        return self.admin_service.most_requested_dishes()
