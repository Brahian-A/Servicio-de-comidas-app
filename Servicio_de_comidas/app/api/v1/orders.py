# app/api/v1/orders.py

from flask_restx import Namespace, Resource, fields
from flask import request, current_app

api = Namespace('orders', description='Gestión de pedidos')

# Modelos para documentación
dish_item_model = api.model('DishItem', {
    'dish_id': fields.String(required=True),
    'quantity': fields.Integer(default=1)
})

order_input_model = api.model('OrderInput', {
    'user_id': fields.String(required=True),
    'dishes': fields.List(fields.Nested(dish_item_model), required=True)
})

order_output_model = api.model('OrderOutput', {
    'id': fields.String,
    'status': fields.String,
    'total_price': fields.Float,
    'dishes': fields.List(fields.Nested(dish_item_model)),
    'date': fields.String
})


@api.route('/')
class OrderList(Resource):
    @api.expect(order_input_model)
    @api.marshal_with(order_output_model, code=201)
    def post(self):
        """Crear un nuevo pedido bajo demanda"""
        data = request.json
        user_id = data.get('user_id')
        dishes = data.get('dishes', [])

        if not user_id or not dishes:
            api.abort(400, 'user_id y dishes son obligatorios')

        facade = current_app.facade
        order = facade.create_order(user_id, dishes)

        return {
            "id": order.id,
            "status": order.status,
            "total_price": order.total_price,
            "date": order.date.isoformat(),
            "dishes": [
                {"dish_id": od.dish_id, "quantity": od.quantity}
                for od in order.dishes
            ]
        }, 201


@api.route('/<string:user_id>')
class OrderByUser(Resource):
    @api.marshal_list_with(order_output_model)
    def get(self, user_id):
        """Obtener todos los pedidos de un usuario"""
        facade = current_app.facade
        orders = facade.get_orders_by_user(user_id)

        return [
            {
                "id": o.id,
                "status": o.status,
                "total_price": o.total_price,
                "date": o.date.isoformat(),
                "dishes": [
                    {"dish_id": od.dish_id, "quantity": od.quantity}
                    for od in o.dishes
                ]
            }
            for o in orders
        ]
