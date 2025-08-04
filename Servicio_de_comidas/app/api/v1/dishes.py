from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from datetime import datetime

api = Namespace('dishes', description='Endpoints para gestión de platos')

# Modelo para documentación Swagger
dish_model = api.model('Dish', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True),
    'type': fields.String(required=True, description="desayuno, almuerzo o cena"),
    'description': fields.String,
    'price': fields.Float(required=True),
    'available_on_date': fields.String(description='Formato YYYY-MM-DD'),
})


@api.route('/')
class DishList(Resource):
    @api.marshal_list_with(dish_model)
    def get(self):
        """Obtener todos los platos"""
        facade = current_app.facade
        return facade.dish_service.repo.get_all()

    @api.expect(dish_model)
    @api.marshal_with(dish_model, code=201)
    def post(self):
        """Crear un nuevo plato"""
        data = request.json
        facade = current_app.facade

        available_date = None
        if data.get('available_on_date'):
            try:
                available_date = datetime.fromisoformat(data['available_on_date']).date()
            except ValueError:
                api.abort(400, 'Fecha inválida, formato debe ser YYYY-MM-DD')

        dish = facade.create_dish(
            name=data['name'],
            type=data['type'],
            description=data.get('description'),
            price=float(data['price']),
            available_on_date=available_date
        )
        return dish, 201


@api.route('/tomorrow')
class DishTomorrow(Resource):
    @api.marshal_list_with(dish_model)
    def get(self):
        """Obtener platos disponibles para mañana"""
        facade = current_app.facade
        return facade.get_dishes_for_tomorrow()
