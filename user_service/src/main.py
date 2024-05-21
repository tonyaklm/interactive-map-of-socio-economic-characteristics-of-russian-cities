from flask import Flask, redirect, url_for, request

from blueprints import user
from flask import render_template
from config import settings
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os
import requests

app = Flask(__name__, template_folder="templates")

app.register_blueprint(user.blueprint)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.sqlalchemy_database_uri
app.config['SECRET_KEY'] = settings.secret_key

app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
# app.config['JWT_COOKIE_SECURE'] = True
# app.config['JWT_ACCESS_COOKIE_PATH'] = os.getenv('USER_SERVICE_URL') + '/get_token/'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=5)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

jwt = JWTManager(app)

# @jwt.unauthorized_loader
# def my_invalid_token_callback(expired_token):
#     return redirect(url_for('user.login'))

@app.route('/')
def home():
    return render_template('main.html')

# @app.before_request
# def check_jwt_token():
#     if request.cookies.get('access_token_cookie') is None:
#         return redirect(url_for('user.login'))
#
# @app.after_request
# def check_jwt_token(response):
#     if request.cookies.get('access_token_cookie') is None:
#         return redirect(url_for('user.login'))
#     return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
