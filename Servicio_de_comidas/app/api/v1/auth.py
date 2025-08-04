from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    def post(self):
        """Login and get a JWT token"""
        data = api.payload
        user = facade.get_user_by_email(data['email'])

        if not user or not user.verify_password(data['password']):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(identity=user.id)
        return {
            'access_token': access_token,
            'user_id': user.id
        }, 200
