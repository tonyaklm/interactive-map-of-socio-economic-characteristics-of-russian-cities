from passlib.apps import custom_app_context as pwd_context
from db import Base
from flask_jwt_extended import create_access_token, create_refresh_token
from sqlalchemy import Column, Integer, String, Boolean


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False, unique=True)
    login = Column(String(60), nullable=False, unique=True)
    password_hash = Column(String(256), unique=True)
    admin = Column(Boolean, default=False)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def get_token(self):
        additional_claims = {"is_admin": self.admin}
        return create_access_token(identity=self.id, additional_claims=additional_claims), create_refresh_token(identity=self.id, additional_claims=additional_claims)
