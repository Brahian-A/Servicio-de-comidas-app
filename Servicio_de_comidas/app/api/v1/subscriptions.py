# app/api/v1/subscriptions.py

from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from datetime import datetime

api = Namespace('subscriptions', description='Planes y suscripciones de comida')

# ---------------------------
# Modelos Swagger
# ---------------------------

subscription_plan_model = api.model('SubscriptionPlan', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True),
    'meals_per_day': fields.Integer(required=True),
    'days_per_week': fields.Integer(required=True),
    'deliveries_per_week': fields.Integer(required=True),
    'price': fields.Float(required=True)
})

subscribe_input_model = api.model('UserSubscribe', {
    'user_id': fields.String(required=True),
    'plan_id': fields.String(required=True),
    'start_date': fields.String(required=True, description='Formato YYYY-MM-DD')
})

scheduled_meal_output = api.model('ScheduledMeal', {
    'id': fields.String,
    'date': fields.String,
    'meal_type': fields.String,
    'dish_id': fields.String
})

assign_dish_model = api.model('AssignDish', {
    'scheduled_meal_id': fields.String(required=True),
    'dish_id': fields.String(required=True)
})


@api.route('/plans')
class SubscriptionPlanList(Resource):
    @api.expect(subscription_plan_model)
    @api.marshal_with(subscription_plan_model, code=201)
    def post(self):
        """Crear un nuevo plan de suscripción"""
        data = request.json
        facade = current_app.facade
        plan = facade.create_subscription_plan(**data)
        return plan, 201

    @api.marshal_list_with(subscription_plan_model)
    def get(self):
        """Listar todos los planes disponibles"""
        facade = current_app.facade
        return facade.subscription_service.get_all_plans()


@api.route('/subscribe')
class UserSubscribe(Resource):
    @api.expect(subscribe_input_model)
    def post(self):
        """Suscribir un usuario a un plan"""
        data = request.json
        try:
            start_date = datetime.fromisoformat(data['start_date']).date()
        except ValueError:
            api.abort(400, 'start_date inválida. Formato: YYYY-MM-DD')

        facade = current_app.facade
        sub = facade.subscribe_user(
            user_id=data['user_id'],
            plan_id=data['plan_id'],
            start_date=start_date
        )
        return {"message": "Suscripción creada", "id": sub.id}, 201


@api.route('/schedule/<string:user_subscription_id>/week')
class ScheduledMeals(Resource):
    @api.marshal_with(scheduled_meal_output, as_list=True)
    def get(self, user_subscription_id):
        """Obtener comidas programadas de la semana"""
        facade = current_app.facade
        return facade.get_user_meals_for_week(user_subscription_id)


@api.route('/schedule/assign')
class AssignDish(Resource):
    @api.expect(assign_dish_model)
    def post(self):
        """Asignar un plato a una comida programada"""
        data = request.json
        facade = current_app.facade
        meal = facade.assign_dish_to_meal(data['scheduled_meal_id'], data['dish_id'])
        if not meal:
            api.abort(404, "Comida o plato no encontrados")
        return {"message": "Plato asignado correctamente"}
