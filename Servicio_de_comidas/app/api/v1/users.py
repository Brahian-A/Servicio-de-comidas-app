from flask_restx import Namespace, Resource, fields
from flask import current_app, request
import re

api = Namespace('users', description='User operations')

# ==================== Validación de Email ====================
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email_format(email):
    if not EMAIL_REGEX.match(email):
        raise ValueError('Formato de correo electrónico inválido.')
    return email

# ==================== Modelos para Swagger y Validación ====================
user_model = api.model('User', {
    'first_name': fields.String(required=True, min_length=1),
    'last_name': fields.String(required=True, min_length=1),
    'email': fields.String(required=True),
    'password': fields.String(required=True, min_length=6),
    'phone': fields.String(required=False),
    'address': fields.String(required=False),
    'preferences': fields.String(required=False),
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(min_length=1),
    'last_name': fields.String(min_length=1),
    'phone': fields.String(),
    'address': fields.String(),
    'preferences': fields.String(),
    # ⚠️ NO ponemos email ni password aquí para evitar edición
})

# ==================== Rutas ====================

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered or invalid input')
    def post(self):
        data = request.json
        facade = current_app.facade

        required_fields = ['email', 'first_name', 'last_name', 'password']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return {
                'status': 'error',
                'message': f'Faltan campos obligatorios: {missing}'
            }, 400

        try:
            validate_email_format(data['email'])
        except ValueError as e:
            return {'status': 'error', 'message': str(e)}, 400
        
        try:
            user = facade.create_user(**data)
            return {
                'status': 'success',
                'message': 'Usuario creado correctamente.',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': user.phone,
                    'address': user.address,
                    'preferences': user.preferences
                        }
            }, 201
        except ValueError as e:
            return {
                'status': 'error',
                'message': str(e)
            }, 409

    @api.response(200, 'All users retrieved')
    def get(self):
        """Get all users"""
        facade = current_app.facade
        users = facade.get_all_users()
        return [user.to_dict() for user in users], 200



@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        facade = current_app.facade
        user = facade.get_user(user_id)
        if not user:
            return {'status': 'error', 'message': 'User not found'}, 404
        return user.to_dict(), 200
    

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user info"""
        updated_data = api.payload
        facade = current_app.facade

        # No permitir modificar email
        if 'email' in updated_data:
            return {
                'error': 'No se permite modificar el email del usuario.'
            }, 400

        # No permitir modificar password
        if 'password' in updated_data:
            return {
                'error': 'No se permite modificar la contraseña desde este endpoint.'
            }, 400

        user = facade.update_user(user_id, updated_data)

        if not user:
            return {'error': 'User not found'}, 404

        return {
            'status': 'success',
            'message': 'Usuario actualizado correctamente.',
            'user': user.to_dict()
        }, 200

    
    @api.response(200, 'User deleted successfully')
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user"""
        facade = current_app.facade
        result = facade.delete_user(user_id)

        if not result:
            return {
                'status': 'error',
                'message': 'Usuario no encontrado.'
            }, 404

        return {
            'status': 'success',
            'message': 'Usuario eliminado correctamente.'
        }, 200


