from app.models.user import User
from app.repositories.base import SQLAlchemyRepository

class UserService:
    def __init__(self, session):
        self.session = session

    def get_by_email(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def create_user(self, email, password):
        user = User(email=email)
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user

    def get_all_users(self):
        return self.session.query(User).all()

    def delete_user(self, user_id):
        user = self.session.query(User).get(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False