import folium
import json
from utils.map import color_region_by_id
from copy import deepcopy

folium_map = folium.Map(location=[69, 88], zoom_start=3, control_scale=True)


def create_default_map():
    with open('shapefiles/russia_geojson.geojson') as response:
        russia = json.load(response)

    folium.GeoJson(
        russia,
        style_function=lambda feature: {
            'fillColor': 'blue',
            'color': 'black',
            'weight': 1,
            'dashArray': '0.2, 0.2'
        }
    ).add_to(folium_map)

    for region in russia['features']:
        region_id = region['properties']['id']
        color_region_by_id(region_id, folium_map)

    folium.LayerControl().add_to(folium_map)


def get_folium_map():
    return deepcopy(folium_map)
