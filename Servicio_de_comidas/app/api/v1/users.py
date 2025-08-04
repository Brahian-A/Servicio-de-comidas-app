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
    'first_name': fields.String(required=True, min_length=1, description='First name of the user'),
    'last_name': fields.String(required=True, min_length=1, description='Last name of the user'),
    'email': fields.String(required=True, min_length=1, description='Email of the user'),
    'password': fields.String(required=True, min_length=6, description='User password')
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(min_length=1, description='First name of the user'),
    'last_name': fields.String(min_length=1, description='Last name of the user'),
    'email': fields.String(min_length=1, description='Email of the user'),
    'password': fields.String(min_length=6, description='User password')
})

# ==================== Rutas ====================

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Email already registered or invalid input')
    def post(self):
        """Register a new user"""
        user_data = api.payload
        facade = current_app.facade

        try:
            validate_email_format(user_data['email'])
        except ValueError as e:
            return {'error': str(e)}, 400

        if 'password' not in user_data or len(user_data['password']) < 6:
            return {'error': 'Password is required and must be at least 6 characters'}, 400

        if facade.get_user_by_email(user_data['email']):
            return {'error': 'Email already registered'}, 400

        new_user = facade.create_user(user_data)
        return new_user, 201

    @api.response(200, 'All users retrieved')
    def get(self):
        """Get all users"""
        facade = current_app.facade
        users = facade.get_users()
        return users, 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID"""
        facade = current_app.facade
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user, 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Invalid input data')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user info"""
        updated_data = api.payload
        facade = current_app.facade

        email = updated_data.get('email')
        if email:
            try:
                validate_email_format(email)
            except ValueError as e:
                return {'error': str(e)}, 400

        password = updated_data.get('password')
        if password and len(password) < 6:
            return {'error': 'Password must be at least 6 characters'}, 400

        updated_user = facade.update_user(user_id, updated_data)
        if isinstance(updated_user, dict) and 'error' in updated_user:
            return updated_user, 400
        if updated_user:
            return updated_user, 200
        return {'error': 'User not found'}, 404

    @api.response(200, 'User deleted successfully') 
    @api.response(404, 'User not found')
    def delete(self, user_id):
        """Delete user"""
        facade = current_app.facade
        result = facade.delete_user(user_id)
        if 'error' in result:
            if result['error'] == 'User not found':
                return result, 404
            else:
                return result, 400
        return result, 200
