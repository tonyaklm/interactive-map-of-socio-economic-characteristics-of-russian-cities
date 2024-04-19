from passlib.apps import custom_app_context as pwd_context
from app import db
from flask_jwt_extended import create_access_token


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    login = db.Column(db.String(60), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), unique=True)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def get_token(self):
        return create_access_token(identity=self.id)
