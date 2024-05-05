import math
from typing import List, Dict

import folium
import json
from utils.map import color_region_by_id
from branca.colormap import linear


class FoliumMap:
    def __init__(self, indicator: str = "Empty_Map"):
        self.map = folium.Map(location=[55, 37], zoom_start=7, control_scale=True)
        self.colormap = None
        self.create()
        self.indicator = indicator
        self.template_name = "static/{}.html".format(self.indicator)

    def create(self) -> None:
        with open('../shapefiles/russia_geojson.geojson') as response:
            russia = json.load(response)

        folium.GeoJson(
            russia,
            style_function=lambda feature: {
                'fillColor': 'blue',
                'color': 'black',
                'weight': 1,
                'dashArray': '0.2, 0.2'
            }
        ).add_to(self.map)

        for region in russia['features']:
            region_id = region['properties']['id']
            color_region_by_id(region_id, self.map)

        folium.LayerControl().add_to(self.map)

    def add_marker(self, item: Dict) -> None:
        str_popup = str(item["settlement"]) + ", " + str(item['region'])
        popup_text = f'{str_popup}, \n' \
                     f'{self.indicator}: {str(item[self.indicator])}'

        str_tooltip = f'<b>{item["settlement"]}</b><br>{self.indicator}: {str(item[self.indicator])}'

        iframe = folium.IFrame(popup_text,
                               width=200,
                               height=100)

        folium_popup = folium.Popup(iframe, min_width=200, max_width=300)

        marker_color = 'while'
        if not math.isnan(item[self.indicator]):
            marker_color = self.colormap(item[self.indicator])

        marker = folium.CircleMarker([item["latitude_dd"], item["longitude_dd"]],
                                     radius=10,
                                     popup=folium_popup,
                                     tooltip=str_tooltip,
                                     fill=True, color=marker_color,
                                     fill_color=marker_color,
                                     fill_opacity=1.0).add_to(self.map)
        self.map.keep_in_front(marker)

    def add_colormap(self, data: List[Dict]) -> None:
        min_value = 1e9
        max_value = -1e9
        for row in data:
            if not math.isnan(row[self.indicator]):
                min_value = min(row[self.indicator], min_value)
                max_value = max(row[self.indicator], max_value)
        self.colormap = linear.YlGnBu_05.scale(
            min_value,
            max_value
        ).to_step(10)
        self.colormap.caption = self.indicator
        self.map.add_child(self.colormap)

    def save(self):
        self.map.save(self.template_name)
