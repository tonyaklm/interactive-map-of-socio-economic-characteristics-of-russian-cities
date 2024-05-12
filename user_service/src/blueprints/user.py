from datetime import datetime, timezone, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies, get_jwt, \
    create_access_token
from flask import Blueprint
from flask import flash, make_response, session
from flask_jwt_extended import get_jwt, create_access_token, get_jwt_identity, set_access_cookies, set_refresh_cookies, \
    create_refresh_token, unset_jwt_cookies
from utils.forms import LoginForm, RegisterForm
from flask import render_template, flash, redirect, request, url_for
from tables.user import User
from db import db_session
from config import settings
from flask import request, jsonify, Response
import requests
import jwt
import os

blueprint = Blueprint('user', __name__, template_folder='templates')
jar = requests.cookies.RequestsCookieJar()


@blueprint.route('/register/', methods=['GET', 'POST'])
# @jwt_required()
def register():
    # user_id = get_jwt_identity()
    token = request.cookies.get('access_token_cookie')
    if not token:
        return redirect(url_for('user.login'))
    else:
        try:
            data = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=['HS256'])
            user_id = data['user_id']
            user = db_session.query(User).filter_by(id=user_id).first()
            if user and user.admin:
                form = RegisterForm(request.form)
                if request.method == 'POST' and form.validate():
                    if db_session.query(User).filter_by(login=form.login.data).first() is None:
                        new_user = User(username=form.username.data, login=form.login.data, admin=form.admin.data)
                        new_user.hash_password(form.password.data)
                        db_session.add(new_user)
                        db_session.commit()

                        flash('Вы успешно зарегистрировали нового пользователя', 'success')
                        return render_template('register.html', form=RegisterForm())
                    else:
                        flash('Пользователь с таким Login уже существует', 'error')
                        return render_template('register.html', form=form)
                else:
                    return render_template('register.html', form=form)
            else:
                # flash('У Вас нет доступа к регистрации новых пользователей', 'error')
                map_address = settings.data_service_address + '/map/'
                return redirect(map_address)
        except jwt.ExpiredSignatureError:
            return redirect(url_for('user.login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('user.login'))


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    map_address = settings.data_service_address + '/map/'

    if request.method == 'POST' and form.validate():
        user = db_session.query(User).filter_by(login=form.login.data).first()
        if user is None:
            flash('Неверный Login пользователя', 'error')
            return render_template('login.html', form=form)
        else:
            if user is not None and user.verify_password(form.password.data):
                access_token = user.get_token()

                response = make_response(redirect(map_address, code=302))

                response.set_cookie(key='access_token_cookie', value=access_token)
                # set_access_cookies(response, access_token)
                # set_refresh_cookies(response, refresh_token)
                # response.set_cookie('access_token_cookie', access_token)

                return response
            else:
                flash('Неверный Password пользователя', "error")
                return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)


@blueprint.route('/get_token/', methods=['GET'])
def get_token():
    if request.method == 'GET':
            token = request.cookies.get('access_token_cookie')
            if not token:
                print("here")
                return Response("Access token not found", status=401)
            else:
                try:
                    data = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=['HS256'])
                    is_login = True
                    is_admin = data.get('is_admin', False)
                    return {'is_admin': is_admin, 'is_login': is_login}, 200
                except jwt.ExpiredSignatureError:
                    print(3)
                    return Response("ExpiredSignatureError", status=402)
                except jwt.InvalidTokenError:
                    print(2)
                    return Response("InvalidTokenError", status=403)
    else:
        print(request)
        return Response("Unsupported method", status=404)



# @blueprint.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=300))
#
#         # map_address = settings.data_service_address + '/map/'
#         # response = make_response(redirect(map_address, code=302))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             refresh_token = create_refresh_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#             set_refresh_cookies(response, refresh_token)
#         return response
#     except (RuntimeError, KeyError):
#         return response

@blueprint.route('/logout/')
# @jwt_required()
def logout():
    token = request.cookies.get('access_token_cookie')
    if not token:
        return redirect(url_for('user.login'))
    else:
        try:
            data = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=['HS256'])
            map_address = settings.data_service_address + '/map/'
            response = make_response(redirect(map_address, code=302))
            response.delete_cookie("access_token_cookie")
            # response.delete_cookie("refresh_token_cookie")
            return response
        except jwt.ExpiredSignatureError:
            return redirect(url_for('user.login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('user.login'))
