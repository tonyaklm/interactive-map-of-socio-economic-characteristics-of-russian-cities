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
from app.map import color_region_by_id, data, add_circle_marker, add_marker

cur_map_name = "map"

@app.route("/")
def render_map():
    print(os.listdir("../map/templates"))
    folium_map = folium.Map(location=[69, 88], zoom_start=3, control_scale=True)
    # data.apply(add_marker, axis=1, args=(folium_map,))

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


@app.route('/indicator')
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
        data.apply(add_circle_marker, axis=1, args=(folium_map, indicator,))

    cur_map_name = 'map_' + indicator
    filename = cur_map_name + '.html'
    folium_map.save(f"templates/{filename}")

    return render_template('index.html', selected=indicator)
