import colordict as colordict
from IPython.display import display
from flask import Flask, render_template
import folium
import geopandas as gpd
import pandas as pd
import folium
import branca
import requests
import json
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup

# from osgeo import gdal
from sqlalchemy.dialects import plugins

app = Flask(__name__)

data = pd.read_csv('shapefiles/icsid_cities.csv')
colors = list(set(data['region'].values))
colors_names = [
    'lightgreen', 'darkblue', 'blue', 'orange', 'cadetblue', 'darkpurple', 'beige', 'green', 'darkred', 'lightblue',
    'white', 'darkgreen', 'lightgray', 'black', 'purple', 'pink', 'red', 'gray', 'lightred'
]

dict_colors = {}
j = 0
for i in range(len(colors)):
    if j == len(colors_names):
        j = 0
    dict_colors[colors[i]] = colors_names[j]
    j += 1


def add_marker(row, folium_map):  # маркеры в виде геометок
    str_popup = str(row["settlement"]) + " " + str(row['region'])
    folium.Marker([row["latitude_dd"], row["longitude_dd"]], icon=folium.Icon(dict_colors[row['region']]),
                  popup=str_popup).add_to(folium_map)


def add_circle_marker(row, folium_map):  # маркеры в виде кружков в пропорции с населением
    str_popup = str(row["settlement"]) + " " + str(row['region'])

    popup_text = f'''{str_popup}
        Population: {str(row["population"])}'''

    iframe = folium.IFrame(popup_text,
                           width=100,
                           height=100)

    folium_popup = folium.Popup(iframe, max_width=int(0.00002 * int(row["population"])))

    folium.CircleMarker([row["latitude_dd"], row["longitude_dd"]],
                        radius=0.00002 * int(row["population"]),  # пропорция по population
                        popup=folium_popup,
                        fill=True, color=dict_colors[row['region']],
                        fill_color=dict_colors[row['region']],
                        fill_opacity=0.7).add_to(folium_map)


@app.route("/")
def render_map():
    folium_map = folium.Map(location=[50, 77], zoom_start=3, control_scale=True)
    data.apply(add_circle_marker, axis=1, args=(folium_map,))

    with open('shapefiles/russia_geojson.geojson') as response:
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

    region_geojson = {
        "type": "FeatureCollection",
        "features": [feature for feature in russia['features'] if feature['properties']['id'] == 25]
    }

    folium.GeoJson(region_geojson,
                   style_function=lambda feature: {
                       'fillColor': 'red',
                       'color': 'red',
                       'weight': 2,
                       'fillOpacity': 0.5,
                   }).add_to(folium_map)
    tile_layer = folium.TileLayer('Камчатский край', attr='OpenStreetMap')
    tile_layer.add_to(folium_map)

    tile_layer.add_to(folium_map)

    folium.LayerControl().add_to(folium_map)

    folium_map.save("templates/map.html")
    return render_template('map.html')


##ВИКА


# folium.Choropleth(
#     geo_data=russia,
#     data=data,
#     columns=["region", "population"],
#     # key_on="feature.id",
#     fill_color="YlGn",
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     legend_name="Population Rate",
# ).add_to(map)
# #
# folium.LayerControl().add_to(map)

# gdal.SetConfigOption('SHAPE_RESTORE_SHX', 'YES')
# gdf = gpd.read_file('shapefiles/gadm41_RUS_1.shp')
# with open('shapefiles/gadm41_RUS_1.json') as response:
#     russia = json.load(response)
# white_tile = branca.utilities.image_to_url([[2, 2], [2, 2]])
# f = folium.Figure(width=500, height=500)
# m = folium.Map(location=[50, 77], maxZoom=400, minZoom=1, zoom_control=True, zoom_start=2,
#                scrollWheelZoom=True, tiles=white_tile, attr='white tile',
#                dragging=True).add_to(f)
# # folium.Marker([65.25, 94.15], popup='Russia')
# popup = GeoJsonPopup(
#     fields=['NAME_1', 'GID_1'],
#     # aliases=['State', "Data points"],
#     localize=True,
#     labels=True,
#     style="background-color: yellow;",
# )
# tooltip = GeoJsonTooltip(
#     fields=['NAME_1', 'GID_1'],
#     # aliases=['State', "Data points"],
#     localize=True,
#     sticky=False,
#     labels=True,
#     style="""
#         background-color: #F0EFEF;
#         border: 1px solid black;
#         border-radius: 1px;
#         box-shadow: 3px;
#     """,
#     max_width=1000,
# )
# # Add choropleth layer
# g = folium.Choropleth(
#     geo_data=russia,
#     data=gdf,
#     columns=['NAME_1', 'GID_1'],
#     # key_on='properties.st_nm',
#     fill_color='YlGn',
#     fill_opacity=0.4,
#     line_opacity=0.4,
#     # legend_name='Data Points',
#     highlight=True,
#
# ).add_to(m)
# folium.GeoJson(
#     russia,
#     style_function=lambda feature: {
#         'fillColor': '#ffff00',
#         'color': 'black',
#         'weight': 0.2,
#         'dashArray': '5, 5'
#     },
#     tooltip=tooltip,
#     popup=popup).add_to(g)

if __name__ == '__main__':
    app.run(debug=True)
