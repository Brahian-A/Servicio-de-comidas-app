from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from datetime import datetime

subscription_ns = Namespace('subscriptions', description='User subscriptions & plans')

# --- MODELOS (Swagger) ---
plan_model = subscription_ns.model('SubscriptionPlan', {
    'id': fields.String(readOnly=True),
    'name': fields.String(required=True),
    'meals_per_day': fields.Integer(required=True, min=1),
    'days_per_week': fields.Integer(required=True, min=1, max=7),
    'deliveries_per_week': fields.Integer(required=True, min=1, max=7),
    'price': fields.Float(required=True),
})

plan_create_model = subscription_ns.model('SubscriptionPlanCreate', {
    'name': fields.String(required=True),
    'meals_per_day': fields.Integer(required=True, min=1),
    'days_per_week': fields.Integer(required=True, min=1, max=7),
    'deliveries_per_week': fields.Integer(required=True, min=1, max=7),
    'price': fields.Float(required=True),
})

plan_update_model = subscription_ns.model('SubscriptionPlanUpdate', {
    'name': fields.String,
    'meals_per_day': fields.Integer(min=1),
    'days_per_week': fields.Integer(min=1, max=7),
    'deliveries_per_week': fields.Integer(min=1, max=7),
    'price': fields.Float,
})

subscription_model = subscription_ns.model('UserSubscription', {
    'id': fields.String(readOnly=True),
    'user_id': fields.String(required=True),
    'plan_id': fields.String(required=True),
    'start_date': fields.String(required=True, description='YYYY-MM-DD'),
    'end_date': fields.String(required=True),
    'meals_remaining': fields.Integer(required=True),
    'next_delivery_dates': fields.List(fields.String),
    'is_active': fields.Boolean,
    'is_paused': fields.Boolean,
})

subscription_create_model = subscription_ns.model('UserSubscriptionCreate', {
    'user_id': fields.String(required=True),
    'plan_id': fields.String(required=True),
    'start_date': fields.String(required=True, description='YYYY-MM-DD'),
    'weeks': fields.Integer(required=False, description='Duración en semanas (default 4)')
})

# --- RUTAS PLANES ---
@subscription_ns.route('/plans')
class Plans(Resource):
    @subscription_ns.marshal_list_with(plan_model, code=200, envelope='items')
    def get(self):
        svc = current_app.facade.subscription_service
        return svc.list_plans()

    @subscription_ns.expect(plan_create_model, validate=True)
    @subscription_ns.marshal_with(plan_model, code=201)
    def post(self):
        svc = current_app.facade.subscription_service
        try:
            return svc.create_plan(**request.json), 201
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/plans/<string:plan_id>')
class PlanDetail(Resource):
    @subscription_ns.marshal_with(plan_model, code=200)
    def get(self, plan_id):
        svc = current_app.facade.subscription_service
        plan = svc.get_plan(plan_id)
        if not plan:
            subscription_ns.abort(404, "Plan not found")
        return plan

    @subscription_ns.expect(plan_update_model, validate=True)
    @subscription_ns.marshal_with(plan_model, code=200)
    def put(self, plan_id):
        svc = current_app.facade.subscription_service
        try:
            return svc.update_plan(plan_id, **request.json)
        except ValueError as e:
            # nombre duplicado o not found
            subscription_ns.abort(400, str(e))

    def delete(self, plan_id):
        svc = current_app.facade.subscription_service
        try:
            svc.delete_plan(plan_id)
            return {'message': 'Plan deleted'}, 200
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/')
class Subscriptions(Resource):
    @subscription_ns.expect(subscription_create_model, validate=True)
    @subscription_ns.marshal_with(subscription_model, code=201)
    def post(self):
        svc = current_app.facade.subscription_service
        payload = request.json
        from datetime import datetime as dt
        try:
            start_date = dt.strptime(payload['start_date'], '%Y-%m-%d').date()
            weeks = int(payload.get('weeks', 4))
            return svc.assign_plan_to_user(payload['user_id'], payload['plan_id'], start_date, weeks), 201
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/user/<string:user_id>')
class UserSubscriptions(Resource):
    @subscription_ns.marshal_list_with(subscription_model, code=200, envelope='items')
    def get(self, user_id):
        svc = current_app.facade.subscription_service
        return svc.list_user_subscriptions(user_id)

@subscription_ns.route('/<string:subscription_id>')
class SubscriptionDetail(Resource):
    @subscription_ns.marshal_with(subscription_model, code=200)
    def get(self, subscription_id):
        svc = current_app.facade.subscription_service
        sub = svc.get_subscription(subscription_id)
        if not sub:
            subscription_ns.abort(404, "Subscription not found")
        return sub

@subscription_ns.route('/<string:subscription_id>/pause')
class SubscriptionPause(Resource):
    @subscription_ns.marshal_with(subscription_model, code=200)
    def post(self, subscription_id):
        svc = current_app.facade.subscription_service
        try:
            return svc.pause_subscription(subscription_id)
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/<string:subscription_id>/resume')
class SubscriptionResume(Resource):
    @subscription_ns.marshal_with(subscription_model, code=200)
    def post(self, subscription_id):
        svc = current_app.facade.subscription_service
        try:
            return svc.resume_subscription(subscription_id)
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/<string:subscription_id>/cancel')
class SubscriptionCancel(Resource):
    @subscription_ns.marshal_with(subscription_model, code=200)
    def post(self, subscription_id):
        svc = current_app.facade.subscription_service
        try:
            return svc.cancel_subscription(subscription_id)
        except ValueError as e:
            subscription_ns.abort(400, str(e))

@subscription_ns.route('/<string:subscription_id>/consume')
class SubscriptionConsume(Resource):
    @subscription_ns.expect(subscription_ns.model('ConsumeBody', {
        'date': fields.String(required=False, description='YYYY-MM-DD (opcional)'),
    }), validate=True)
    @subscription_ns.marshal_with(subscription_model, code=200)
    def post(self, subscription_id):
        svc = current_app.facade.subscription_service
        payload = request.json or {}
        target_date = None
        if 'date' in payload and payload['date']:
            from datetime import datetime
            target_date = datetime.strptime(payload['date'], '%Y-%m-%d').date()
        try:
            return svc.register_meal_consumption(subscription_id, target_date)
        except ValueError as e:
            subscription_ns.abort(400, str(e))
