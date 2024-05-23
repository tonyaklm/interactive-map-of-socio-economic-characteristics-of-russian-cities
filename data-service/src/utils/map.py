import folium
import json
from folium import Map
from common.repository import repo
from sqlalchemy.ext.asyncio import AsyncSession
from tables.data import DataDao

colors_names = [
    'lightgreen', 'darkblue', 'blue', 'orange', 'cadetblue', 'beige', 'green', 'darkred', 'lightblue', 'darkgreen',
    'purple', 'pink', 'gray', 'lightred'
]


async def color_region_by_id(id_region: int, geojson_layer: folium.FeatureGroup, session: AsyncSession):
    with open(f'shapefiles/russia_region_{id_region}.geojson') as response:
        region_geojson = json.load(response)
    region = await repo.select_indicators([DataDao.region], [DataDao.region_id == id_region], session)
    name_region = region.scalars().all()[0]
    str_tooltip = f'<b>{name_region}</b>'
    str_popup = f'<b>Регион:</b> {name_region}'
    folium.GeoJson(region_geojson,
                   style_function=lambda feature: {
                       'fillColor': colors_names[id_region % len(colors_names)],
                       'color': "black",
                       'weight': 1,
                       'fillOpacity': 0.2,
                   },
                   name=name_region,
                   tooltip=str_tooltip,
                   popup=folium.Popup(str_popup)).add_to(geojson_layer)
