from flask import Flask, render_template
from flask import request
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

app = Flask(__name__, template_folder="../templates")

from app import map
from app import routes