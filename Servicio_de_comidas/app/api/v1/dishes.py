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
    'is_active': fields.Boolean(readonly=True)
})

# Modelo para mensajes de error
error_model = api.model('ErrorResponse', {
    'status': fields.String,
    'error': fields.String,
    'message': fields.String,
    'missing': fields.List(fields.String, required=False),
    'details': fields.String(required=False),
})


@api.route('/')
class DishList(Resource):
    @api.marshal_list_with(dish_model)
    def get(self):
        """Obtener todos los platos"""
        return current_app.facade.dish_service.repo.get_all()

    @api.expect(dish_model)
    @api.response(201, 'Plato creado exitosamente', dish_model)
    @api.response(400, 'Error de validación', error_model)
    @api.response(409, 'Plato duplicado', error_model)
    def post(self):
        """Crear un nuevo plato"""
        data = request.json
        facade = current_app.facade

        # Validar campos obligatorios
        required_fields = ['name', 'type', 'price', 'available_on_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                'status': 'error',
                'error': 'missing_fields',
                'message': 'Faltan campos obligatorios.',
                'missing': missing_fields
            }, 400

        # Validar precio
        try:
            data['price'] = float(data['price'])
        except (ValueError, TypeError):
            return {
                'status': 'error',
                'error': 'invalid_price',
                'message': 'El precio debe ser un número.'
            }, 400

        # Validar fecha
        try:
            data['available_on_date'] = datetime.fromisoformat(data['available_on_date']).date()
        except (ValueError, TypeError):
            return {
                'status': 'error',
                'error': 'invalid_date',
                'message': 'Fecha inválida. Formato requerido: YYYY-MM-DD.'
            }, 400

        # Crear plato
        try:
            new_dish = facade.create_dish(**data)
            return {
                'id': new_dish.id,
                'name': new_dish.name,
                'type': new_dish.type,
                'description': new_dish.description,
                'price': new_dish.price,
                'available_on_date': new_dish.available_on_date.isoformat(),
                'is_active': new_dish.is_active,
            }, 201

        except ValueError as e:
            return {
                'status': 'error',
                'error': 'duplicate_dish',
                'message': 'El plato ya existe para esa fecha.',
                'details': str(e)
            }, 409


@api.route('/tomorrow')
class DishTomorrow(Resource):
    @api.marshal_list_with(dish_model)
    def get(self):
        """Obtener platos disponibles para mañana"""
        return current_app.facade.get_dishes_for_tomorrow()
