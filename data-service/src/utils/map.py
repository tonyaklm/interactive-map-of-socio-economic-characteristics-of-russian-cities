from typing import List, Dict

import folium
import json
import math

import numpy as np
from branca.colormap import linear, LinearColormap
from folium import Map

colors_names = [
    'lightgreen', 'darkblue', 'blue', 'orange', 'cadetblue', 'darkpurple', 'beige', 'green', 'darkred', 'lightblue',
    'white', 'darkgreen', 'lightgray', 'black', 'purple', 'pink', 'red', 'gray', 'lightred'
]


def color_region_by_id(id_region: int, folium_map: Map):
    with open(f'shapefiles/russia_region_{id_region}.geojson') as response:
        region_geojson = json.load(response)
    name_region = region_geojson['features'][0]['properties']['full_name']
    str_tooltip = f'<b>{name_region}</b>'
    folium.GeoJson(region_geojson,
                   style_function=lambda feature: {
                       'fillColor': colors_names[id_region % 10],
                       'color': colors_names[id_region % 10],
                       'weight': 2,
                       'fillOpacity': 0.5,
                   },
                   name=name_region,
                   tooltip=str_tooltip,
                   popup=folium.GeoJsonPopup(fields=['name'],
                                             aliases=["Регион: "],
                                             localize=True,
                                             labels=True)).add_to(folium_map)