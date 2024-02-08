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


@app.route("/")
def render_map():
    # gdal.SetConfigOption('SHAPE_RESTORE_SHX', 'YES')
    gdf = gpd.read_file('shapefiles/gadm41_RUS_1.shp')
    with open('shapefiles/gadm41_RUS_1.json') as response:
        russia = json.load(response)
    white_tile = branca.utilities.image_to_url([[2, 2], [2, 2]])
    f = folium.Figure(width=500, height=500)
    m = folium.Map(location=[50, 77], maxZoom=400, minZoom=1, zoom_control=True, zoom_start=2,
                   scrollWheelZoom=True, tiles=white_tile, attr='white tile',
                   dragging=True).add_to(f)
    # folium.Marker([65.25, 94.15], popup='Russia')

    df_cities = pd.read_csv('cities_data/icsid_cities.csv', encoding='utf8')

    # for row in df_cities.itertuples():
    #     folium.Marker(
    #         location=[float(row.latitude_dd), float(row.longitude_dd)],
    #         popup=row.population,
    #         tooltip=row.settlement
    #     ).add_to(m)

    df_cities = df_cities.sort_values(by='population')

    for lat, long, index, poplulation in zip(df_cities.latitude_dd, df_cities.longitude_dd, df_cities.index,
                                             df_cities.population):
        # print(index)
        folium.CircleMarker([lat, long],
                            radius=0.01 * (index + 2),
                            popup='Population:' + str(poplulation),
                            fill=True, color='r',
                            fill_color='red' if index < 500 else 'green',
                            fill_opacity=0.7).add_to(m)

    tile_layer = folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        max_zoom=19,
        name='darkmatter',
        control=False,
        opacity=0.7
    )
    tile_layer.add_to(m)

    popup = GeoJsonPopup(
        fields=['NL_NAME_1', 'GID_1'],
        # aliases=['State', "Data points"],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )
    tooltip = GeoJsonTooltip(
        fields=['NL_NAME_1', 'GID_1'],
        # aliases=['State', "Data points"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 1px solid black;
            border-radius: 1px;
            box-shadow: 3px;
        """,
        max_width=1000,
    )
    # Add choropleth layer
    g = folium.Choropleth(
        geo_data=russia,
        data=gdf,
        columns=['NL_NAME_1', 'GID_1'],
        # key_on='properties.st_nm',
        fill_color='YlGn',
        fill_opacity=0.4,
        line_opacity=0.4,
        # legend_name='Data Points',
        highlight=True,

    ).add_to(m)
    folium.GeoJson(
        russia,
        style_function=lambda feature: {
            'fillColor': '#ffff00',
            'color': 'black',
            'weight': 0.2,
            'dashArray': '5, 5'
        },
        tooltip=tooltip,
        popup=popup).add_to(g)
    folium.LayerControl().add_to(m)

    # layer = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    #
    # folium.raster_layers.TileLayer(
    #     tiles=layer, name="OpenStreetMap", attr="attribution"
    # ).add_to(m)  # added other countries
    # # add layer control to show different maps
    # folium.LayerControl().add_to(m)
    # m._repr_html_()
    # return f
    m.save("templates/map.html")
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)
