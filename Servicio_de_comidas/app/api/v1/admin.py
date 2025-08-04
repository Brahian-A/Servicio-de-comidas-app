# app/api/v1/admin.py

from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from datetime import datetime

api = Namespace('admin', description='Estadísticas internas del sistema')

dish_count_model = api.model('DishCount', {
    'dish_id': fields.String,
    'count': fields.Integer
})

top_dish_model = api.model('TopDish', {
    'dish_id': fields.String,
    'count': fields.Integer
})


@api.route('/dish-count/<string:date_str>')
class DishCountByDate(Resource):
    @api.marshal_with(dish_count_model, as_list=True)
    def get(self, date_str):
        """Cantidad de veces que se debe preparar cada plato para una fecha"""
        try:
            date_ = datetime.fromisoformat(date_str).date()
        except ValueError:
            api.abort(400, "Fecha inválida. Usar YYYY-MM-DD")

        facade = current_app.facade
        counts = facade.get_dish_count_for_day(date_)
        return [{'dish_id': k, 'count': v} for k, v in counts.items()]


@api.route('/top-dishes')
class TopDishes(Resource):
    @api.marshal_with(top_dish_model, as_list=True)
    def get(self):
        """Top 5 platos más pedidos (por pedidos bajo demanda)"""
        facade = current_app.facade
        raw = facade.get_top_dishes()
        return [{'dish_id': r[0], 'count': r[1]} for r in raw]
