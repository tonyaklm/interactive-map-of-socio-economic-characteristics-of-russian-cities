from app import app
from flask import Flask, render_template
from flask import request
import folium
import geopandas as gpd
import pandas as pd
import folium
import branca
import requests
import json
import os
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup
from app.map import color_region_by_id, data, add_circle_marker, add_marker, add_colorbar
from app.forms import LoginForm, RegisterForm
from flask import Flask, render_template, flash, redirect, request, session, logging, url_for
from app.models import User
from app import db


cur_map_name = "map"


@app.route('/')
def home():
    return render_template('main.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        if User.query.filter_by(login=form.login.data).first() is None:
            new_user = User(username=form.username.data, login=form.login.data)
            new_user.hash_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()

            # access_token = new_user.get_token()
            # response = jsonify({'message': f'User-{new_user.username} registered successfully'})
            # set_access_cookies(response, access_token)
            # return response, 201
            flash('You have successfully registered', 'success')
            return redirect(url_for('login'))
        else:
            # return jsonify({'message': 'Existing user'}), 400
            flash('Such login already exists', 'fail')
            return redirect(url_for('login'))
    else:
        return render_template('register.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate:
        user = User.query.filter_by(login=form.login.data).first()
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
                return redirect(url_for('render_map'))
            else:
                # return jsonify({'message': 'Invalid password'}), 401
                flash('Login or Password Incorrect', "Danger")

                return redirect(url_for('login'))
    return render_template('login.html', form=form)
#     
# @app.after_request
# def refresh_expiring_jwts(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         return response
#     

@app.route("/map/")
def render_map():
    # print(os.listdir("../map/templates"))
    folium_map = folium.Map(location=[69, 88], zoom_start=3, control_scale=True)
    colormap = add_colorbar(folium_map, "Population")
    data.apply(add_circle_marker, axis=1, args=(folium_map, "Population", colormap,))

    with open('../map/shapefiles/russia_geojson.geojson') as response:
        russia = json.load(response)

    folium.GeoJson(
        russia,
        style_function=lambda feature: {
            'fillColor': 'blue',
            'color': 'black',
            'weight': 1,
            'dashArray': '0.2, 0.2'
        },
        # tooltip=tooltip,
    ).add_to(folium_map)

    for region in russia['features']:
        region_id = region['properties']['id']
        color_region_by_id(region_id, folium_map)

    folium.LayerControl().add_to(folium_map)

    folium_map.save("templates/map.html")

    return render_template('index.html', selected='Empty Map')
    # return render_template('map.html')


@app.route('/map')
def map():
    filename = f'{cur_map_name}.html'
    return render_template(filename)


@app.route('/indicator/')
def chosen_indicator():
    global cur_map_name

    indicator = request.args.get('indicator')
    print(indicator)

    folium_map = folium.Map(location=[69, 88], zoom_start=3, control_scale=True)

    with open('../map/shapefiles/russia_geojson.geojson') as response:
        russia = json.load(response)

    folium.GeoJson(
        russia,
        style_function=lambda feature: {
            'fillColor': 'blue',
            'color': 'black',
            'weight': 1,
            'dashArray': '0.2, 0.2'
        },
        # tooltip=tooltip,
    ).add_to(folium_map)

    for region in russia['features']:
        region_id = region['properties']['id']
        color_region_by_id(region_id, folium_map)

    folium.LayerControl().add_to(folium_map)

    if indicator != 'Empty Map':
        colormap = add_colorbar(folium_map, indicator)
        data.apply(add_circle_marker, axis=1, args=(folium_map, indicator, colormap,))

    cur_map_name = 'map_' + indicator
    filename = cur_map_name + '.html'
    folium_map.save(f"templates/{filename}")

    return render_template('index.html', selected=indicator)
