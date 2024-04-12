from flask import Flask, render_template
import pandas as pd
import folium
import branca
import json
import matplotlib
from branca.colormap import linear

matplotlib.use('Agg')
import plotly.graph_objects as go

app = Flask(__name__)

data = pd.read_csv('shapefiles/icsid_cities.csv')
colors = list(set(data['region'].values))
colors_names = [
    'lightgreen', 'darkblue', 'blue', 'orange', 'cadetblue', 'darkpurple', 'beige', 'green', 'darkred', 'lightblue',
    'white', 'darkgreen', 'lightgray', 'black', 'purple', 'pink', 'red', 'gray', 'lightred'
]

match_region_name_and_id = {'Орловская область': 60, 'Карелия': 10, 'Тыва': 18, 'Курская область': 49,
                            'Волгоградская область': 38, 'Красноярский край': 27, 'Смоленская область': 69,
                            'Алтайский край': 23, 'Хакасия': 20, 'Белгородская область': 35, 'Крым': 12,
                            'Ярославская область': 77, 'Удмуртия': 19, 'Дагестан': 5, 'Еврейская АО': 81, 'Коми': 11,
                            'Московская область': 53, 'Алтай': 4, 'Оренбургская область': 59, 'Омская область': 58,
                            'Рязанская область': 64, 'Адыгея': 1, 'Мордовия': 14, 'Магаданская область': 52,
                            'Башкортостан': 2, 'Ленинградская область': 50, 'Томская область': 72, 'Бурятия': 3,
                            'Кемеровская область': 45, 'Кировская область': 46, 'Тверская область': 71,
                            'Челябинская область': 76, 'Краснодарский край': 26, 'Калининградская область': 43,
                            'Ивановская область': 41, 'Липецкая область': 51, 'Марий Эл': 13,
                            'Нижегородская область': 55, 'Санкт-Петербург': 79, 'Тульская область': 73,
                            'Костромская область': 47, 'Пензенская область': 61, 'Псковская область': 62,
                            'Самарская область': 65, 'Новгородская область': 56, 'Тамбовская область': 70,
                            'Калмыкия': 8, 'Архангельская область': 33, 'Курганская область': 48,
                            'Владимирская область': 37, 'Якутия': 15, 'Иркутская область': 42,
                            'Свердловская область': 68, 'Вологодская область': 39, 'Новосибирская область': 57,
                            'Тюменская область': 74, 'Забайкальский край': 24, 'Сахалинская область': 67,
                            'Мурманская область': 54, 'Северная Осетия': 16, 'Ульяновская область': 75,
                            'Хабаровский край': 31, 'Ненецкий АО': 82, 'Камчатский край': 25,
                            'Ханты-Мансийский АО — Югра': 83, 'Пермский край': 28, 'Саратовская область': 66,
                            'Кабардино-Балкария': 7, 'Воронежская область': 40, 'Карачаево-Черкесия': 9,
                            'Амурская область': 32, 'Брянская область': 36, 'Чувашия': 22, 'Ямало-Ненецкий АО': 85,
                            'Ростовская область': 63, 'Приморский край': 29, 'Севастополь': 80, 'Татарстан': 17,
                            'Калужская область': 44, 'Астраханская область': 34, 'Ставропольский край': 30,
                            'Ингушетия': 6, 'Москва': 78, 'Чечня': 21, 'Чукотка': 84}
match_region_full_name_and_id = {'Орловская область': 60, 'Республика Карелия': 10, 'Республика Тыва': 18,
                                 'Курская область': 49, 'Волгоградская область': 38, 'Красноярский край': 27,
                                 'Смоленская область': 69, 'Алтайский край': 23, 'Республика Хакасия': 20,
                                 'Белгородская область': 35, 'Республика Крым': 12, 'Ярославская область': 77,
                                 'Удмуртская республика ': 19, 'Республика Дагестан': 5, 'Еврейская АО': 81,
                                 'Республика Коми': 11, 'Московская область': 53, 'Республика Алтай': 4,
                                 'Оренбургская область': 59, 'Омская область': 58, 'Рязанская область': 64,
                                 'Республика Адыгея': 1, 'Республика Мордовия': 14, 'Магаданская область': 52,
                                 'Республика Башкортостан': 2, 'Ленинградская область': 50, 'Томская область': 72,
                                 'Республика Бурятия': 3, 'Кемеровская область': 45, 'Кировская область': 46,
                                 'Тверская область': 71, 'Челябинская область': 76, 'Краснодарский край': 26,
                                 'Калининградская область': 43, 'Ивановская область': 41, 'Липецкая область': 51,
                                 'Республика Марий Эл': 13, 'Нижегородская область': 55, 'Санкт-Петербург': 79,
                                 'Тульская область': 73, 'Костромская область': 47, 'Пензенская область': 61,
                                 'Псковская область': 62, 'Самарская область': 65, 'Новгородская область': 56,
                                 'Тамбовская область': 70, 'Республика Калмыкия': 8, 'Архангельская область': 33,
                                 'Курганская область': 48, 'Владимирская область': 37, 'Республика Саха': 15,
                                 'Иркутская область': 42, 'Свердловская область': 68, 'Вологодская область': 39,
                                 'Новосибирская область': 57, 'Тюменская область': 74, 'Забайкальский край': 24,
                                 'Сахалинская область': 67, 'Мурманская область': 54,
                                 'Республика Северная Осетия-Алания': 16, 'Ульяновская область': 75,
                                 'Хабаровский край': 31, 'Ненецкий АО': 82, 'Камчатский край': 25,
                                 'Ханты-Мансийский АО — Югра': 83, 'Пермский край': 28, 'Саратовская область': 66,
                                 'Кабардино-Балкарская Республика': 7, 'Воронежская область': 40,
                                 'Карачаево-Черкесская Республика': 9, 'Амурская область': 32, 'Брянская область': 36,
                                 'Чувашская республика': 22, 'Ямало-Ненецкий АО': 85, 'Ростовская область': 63,
                                 'Приморский край': 29, 'Севастополь': 80, 'Республика Татарстан': 17,
                                 'Калужская область': 44, 'Астраханская область': 34, 'Ставропольский край': 30,
                                 'Республика Ингушетия': 6, 'Москва': 78, 'Чеченская республика': 21,
                                 'Чукотский АО': 84}

dict_colors = {}
j = 0
for i in range(len(colors)):
    if j == len(colors_names):
        j = 0
    dict_colors[colors[i]] = colors_names[j]
    j += 1

colormap = linear.OrRd_03.scale(
    data["population"].min(),
    data["population"].max()
)


def add_marker(row, folium_map):  # маркеры в виде геометок
    str_tooltip = f'<b>{row["settlement"]}</b><br>Население: {str(row["population"])}'
    str_popup = f'''{row["settlement"]}
        Население: {str(row["population"])}'''
    first_year = 2014
    second_year = 2020
    index_name = 'Index100'
    if row["settlement"] == "Москва":
        x = [str(year) for year in range(first_year, second_year)]
        y = [row[f"{index_name}_{year}"] for year in x]
        fig = go.Figure(
            layout=go.Layout(
                title=go.layout.Title(text=f"Значение {index_name} по годам")
            )
        )
        fig['layout']['xaxis']['title'] = 'year'
        fig['layout']['yaxis']['title'] = index_name
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Life expectancy'))

        # Создание HTML для попапа с интерактивным графиком
        html = fig.to_html(full_html=False)

        # Создание попапа с HTML-кодом
        str_popup = folium.Popup(branca.element.IFrame(html, width=700, height=400))

    folium.Marker([row["latitude_dd"], row["longitude_dd"]],
                  icon=folium.Icon(dict_colors[row['region']]),
                  tooltip=str_tooltip,
                  popup=str_popup).add_to(folium_map)


def add_circle_marker(row, folium_map):  # маркеры в виде кружков в пропорции с населением
    str_popup = str(row["settlement"]) + " " + str(row['region'])

    popup_text = f'''{str_popup}
        Население: {str(row["population"])}'''
    str_tooltip = f'<b>{row["settlement"]}</b><br>Население: {str(row["population"])}'

    iframe = folium.IFrame(popup_text,
                           width=100,
                           height=100)

    folium_popup = folium.Popup(iframe, max_width=int(0.00002 * int(row["population"])))

    first_year = 2000
    second_year = 2020
    index_name = 'Index100'

    if row["settlement"] == "Москва":
        x = [str(year) for year in range(first_year, second_year)]
        y = [row[f"{index_name}_{year}"] for year in x]
        fig = go.Figure(
            layout=go.Layout(
                title=go.layout.Title(text=f"Значение {index_name} по годам")
            )
        )
        fig['layout']['xaxis']['title'] = 'year'
        fig['layout']['yaxis']['title'] = index_name
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Life expectancy'))

        # Создание HTML для попапа с интерактивным графиком
        html = fig.to_html(full_html=False)

        # Создание попапа с HTML-кодом
        folium_popup = folium.Popup(branca.element.IFrame(html, width=700, height=400))

    marker = folium.CircleMarker([row["latitude_dd"], row["longitude_dd"]],
                                 radius=10,
                                 popup=folium_popup,
                                 tooltip=str_tooltip,
                                 fill=True, color=colormap(row["population"]),
                                 fill_color=colormap(row["population"]),
                                 fill_opacity=1.0).add_to(folium_map)
    folium_map.keep_in_front(marker)


def color_region_by_id(id_region, folium_map):
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
                   }, show=False,
                   name=name_region,
                   tooltip=str_tooltip,
                   popup=folium.GeoJsonPopup(fields=['name'],
                                             aliases=["Регион: "],
                                             localize=True,
                                             labels=True)).add_to(folium_map)


@app.route("/")
def render_map():
    folium_map = folium.Map(location=[50, 77], zoom_start=3, control_scale=True)
    # data.apply(add_marker, axis=1, args=(folium_map,))
    data.apply(add_circle_marker, axis=1, args=(folium_map,))
    colormap.caption = "Population"
    folium_map.add_child(colormap)

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
    ).add_to(folium_map, )

    for region in russia['features']:
        region_id = region['properties']['id']
        color_region_by_id(region_id, folium_map)

        # сохранение всех регионов в файлы

        # region_geojson = {
        #     "type": "FeatureCollection",
        #     "features": [region]
        # }
        # if region_geojson:
        #     with open(f'shapefiles/russia_region_{region_id}.geojson', 'w') as outfile:
        #         json.dump(region_geojson, outfile)

    folium.LayerControl().add_to(folium_map)

    folium_map.save("templates/map.html")
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
