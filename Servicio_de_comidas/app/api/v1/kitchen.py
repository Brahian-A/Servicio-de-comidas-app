# app/api/v1/kitchen.py

from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from datetime import datetime

api = Namespace('kitchen', description='Operaciones internas para la cocina')

# Modelos Swagger
delivery_model = api.model('DeliveryItem', {
    'name': fields.String,
    'address': fields.String,
    'meal_type': fields.String,
    'dish': fields.Nested(api.model('DishInfo', {
        'name': fields.String,
        'description': fields.String
    }))
})


@api.route('/deliveries/<string:date_str>')
class DailyDeliveries(Resource):
    @api.marshal_with(delivery_model, as_list=True)
    def get(self, date_str):
        """Ver entregas programadas para una fecha (YYYY-MM-DD)"""
        try:
            date_ = datetime.fromisoformat(date_str).date()
        except ValueError:
            api.abort(400, "Formato de fecha inválido (usar YYYY-MM-DD)")

        facade = current_app.facade
        deliveries = facade.get_deliveries_for_date(date_)
        result = []
        for user_id, items in deliveries.items():
            result.extend(items)
        return result
