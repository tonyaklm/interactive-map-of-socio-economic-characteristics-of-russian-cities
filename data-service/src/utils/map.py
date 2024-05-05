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


def add_colorbar(data: List[Dict], folium_map: Map, indicator: str):

    min_value = 1e9
    max_value = -1e9
    for row in data:
        if not math.isnan(row[indicator]):
            min_value = min(row[indicator], min_value)
            max_value = max(row[indicator], max_value)
    colormap = linear.YlGnBu_05.scale(
        min_value,
        max_value
    ).to_step(10)
    colormap.caption = indicator
    folium_map.add_child(colormap)
    return colormap


def add_circle_marker(row: json, folium_map: Map, indicator: str,
                      colormap: LinearColormap):  # маркеры в виде кружков в пропорцией цвета
    str_popup = str(row["settlement"]) + ", " + str(row['region'])

    if indicator == "Population":
        indicator = "population"
    elif indicator == "Children":
        indicator = "children"

    popup_text = f'{str_popup}, \n' \
                 f'{indicator}: {str(row[indicator])}'

    str_tooltip = f'<b>{row["settlement"]}</b><br>{indicator}: {str(row[indicator])}'

    iframe = folium.IFrame(popup_text,
                           width=200,
                           height=100)

    folium_popup = folium.Popup(iframe, min_width=200, max_width=300)
    if math.isnan(row[indicator]):
        str_tooltip = f'<b>{row["settlement"]}</b><br>{indicator} (NaN): {str(row[indicator])}'
        folium.CircleMarker([row["latitude_dd"], row["longitude_dd"]],
                            radius=10,
                            popup=folium_popup,
                            tooltip=str_tooltip,
                            fill=True, color='white',
                            fill_color='white',
                            fill_opacity=1.0).add_to(folium_map)
        return
    marker = folium.CircleMarker([row["latitude_dd"], row["longitude_dd"]],
                                 radius=10,
                                 popup=folium_popup,
                                 tooltip=str_tooltip,
                                 fill=True, color=colormap(row[indicator]),
                                 fill_color=colormap(row[indicator]),
                                 fill_opacity=1.0).add_to(folium_map)
    folium_map.keep_in_front(marker)