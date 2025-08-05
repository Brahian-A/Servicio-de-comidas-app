from app.models.user import User
from app.repositories.base import SQLAlchemyRepository

class UserService:
    def __init__(self, session):
        self.session = session

    def get_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def create_user(self, first_name, last_name, email, password):
        existing_user = self.get_by_email(email)
        if existing_user:
            raise ValueError("Ya existe un usuario con ese email.")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user(self, user_id):
        return self.session.get(User, user_id)

    def get_all_users(self):
        return self.session.query(User).all()

    def delete_user(self, user_id):
        user = self.session.query(User).get(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False
    
    def update_user(self, user_id, updated_data):
        user = self.get_user(user_id)
        if not user:
            return None

        # No permitir modificar el email
        if 'email' in updated_data:
            updated_data.pop('email')

        allowed_fields = ['first_name', 'last_name', 'address', 'phone', 'preferences', 'password']
        for field in allowed_fields:
            if field in updated_data:
                if field == 'password':
                    user.set_password(updated_data['password'])
                else:
                    setattr(user, field, updated_data[field])

        self.session.commit()
        return user
