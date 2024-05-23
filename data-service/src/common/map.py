import math
from typing import Dict, Set
import folium

from sqlalchemy.ext.asyncio import AsyncSession
from utils.map import color_region_by_id
from branca.colormap import linear
from config import settings


class FoliumMap:
    def __init__(self, indicator: str = "Empty_Map"):
        self.map = folium.Map(location=[55, 37], zoom_start=7, control_scale=True)
        self.colormap = None
        self.indicator = indicator
        self.template_name = "static/{}.html".format(self.indicator)
        self.none_markers_layer = folium.FeatureGroup(name='Нулевые маркеры')
        self.geojson_layer = None
        self.markers_layer = None

    async def create(self, region_ids: Set[int], session: AsyncSession) -> None:
        self.geojson_layer = folium.FeatureGroup(name='Регионы')
        for region_id in region_ids:
            await color_region_by_id(region_id, self.geojson_layer, session)
        self.geojson_layer.add_to(self.map)

    async def create_markers_layer(self):
        self.none_markers_layer = folium.FeatureGroup(name='Нулевые маркеры')
        self.markers_layer = folium.FeatureGroup(name='Все маркеры')
        self.none_markers_layer.add_to(self.map)
        self.markers_layer.add_to(self.map)

    async def add_marker(self, item: Dict) -> None:
        tooltip_text = f'Регион: <b>{item["region"]}</b><br>Город: <b>{item["settlement"]}</b>'

        if self.indicator.find('_') != -1:
            indicator_text = f"{self.indicator.split('_')[0]} за {self.indicator.split('_')[1]} год"
        else:
            indicator_text = f"{self.indicator}"

        popup_text = f'Значение <b>{indicator_text}</b> для города <b>{item["settlement"]}</b><br>:' \
                     f' {str(item[self.indicator])}<br><br>' \
                     f'Посмотреть <a href="http://{settings.data_service_address}/dashboard/?id={item["min_municipality_id"]}"' \
                     f' target="_blank">график</a>' \
                     f' индикаторов по годам'

        marker_color = '#000000'
        layer = self.none_markers_layer
        if item[self.indicator] is not None and not math.isnan(item[self.indicator]):
            marker_color = self.colormap(item[self.indicator])
            layer = self.markers_layer

        marker = folium.CircleMarker([item["latitude_dd"], item["longitude_dd"]],
                                     radius=10,
                                     popup=folium.Popup(popup_text, min_width=300, max_width=300),
                                     tooltip=folium.Tooltip(tooltip_text),
                                     fill=True, color=marker_color,
                                     fill_color=marker_color,
                                     fill_opacity=1.0).add_to(layer)
        self.map.keep_in_front(marker)

    async def add_colormap(self, min_value: float, max_value: float) -> None:
        self.colormap = linear.YlGnBu_05.scale(
            min_value,
            max_value
        ).to_step(10)
        self.colormap.caption = self.indicator
        self.map.add_child(self.colormap)

    async def save(self):
        folium.LayerControl().add_to(self.map)
        self.map.save(self.template_name)
