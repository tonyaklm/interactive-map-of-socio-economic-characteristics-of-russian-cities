from datetime import datetime, timezone, timedelta

from flask import Blueprint
from flask_jwt_extended import get_jwt, create_access_token, get_jwt_identity, set_access_cookies
from utils.forms import LoginForm, RegisterForm
from flask import render_template, flash, redirect, request, session, url_for
from tables.user import User
from db import db_session
from config import settings

blueprint = Blueprint('user', __name__, template_folder='templates')


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if db_session.query(User).filter_by(login=form.login.data).first() is None:
            new_user = User(username=form.username.data, login=form.login.data)
            new_user.hash_password(form.password.data)
            db_session.add(new_user)
            db_session.commit()

            # access_token = new_user.get_token()
            # response = jsonify({'message': f'User-{new_user.username} registered successfully'})
            # set_access_cookies(response, access_token)
            # return response, 201
            flash('You have successfully registered', 'success')
            return redirect(url_for('user.login'))
        else:
            # return jsonify({'message': 'Existing user'}), 400
            flash('Such login already exists', 'fail')
            return redirect(url_for('user.login'))
    else:
        return render_template('register.html', form=form)


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    map_address = settings.data_service_address + '/map/'
    print(map_address)

    if request.method == 'POST' and form.validate:
        user = db_session.query(User).filter_by(login=form.login.data).first()
        if user is None:
            # return jsonify({'message': 'Invalid username'}), 401
            return render_template('login.html', form=form)
        else:
            if user is not None and user.verify_password(form.password.data):
                # access_token = user.get_token()
                flash('You have successfully logged in.', "success")
                session['logged_in'] = True
                # session['email'] = user.email
                session['username'] = user.username

                # set_access_cookies(response, access_token)
                # return response, 200
                map_address = settings.data_service_address + '/upload_data/'
                return redirect(map_address, code=302)
            else:
                # return jsonify({'message': 'Invalid password'}), 401
                flash('Login or Password Incorrect', "Danger")

                return redirect(url_for('login'))
    return render_template('login.html', form=form)


@blueprint.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
