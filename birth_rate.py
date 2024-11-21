import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from streamlit_folium import folium_static

# load the birth rate data
df = pd.read_csv('birth_rate.csv', encoding='euc-kr')
df = df.iloc[2:, 0:2]

# change column names
df.columns = ['행정구역별', '출산율']

# if there's a space or a dash, split the word and select the last one
df['행정구역별'] = df['행정구역별'].apply(
    lambda x: x.split()[-1] if ' ' in x else x.split('-')[-1] if '-' in x else x
)

# change the 행정구역별 to 행정구역
df.columns = ['행정구역', '출산율']

# load south korea json data
geo_data = gpd.read_file('BND_SIGUNGU_PG.json').to_crs(epsg=4326)

# select the last word if there's a space between words
geo_data['SIGUNGU_NM'] = geo_data['SIGUNGU_NM'].apply(
    lambda x: x.split()[-1] if ' ' in x else x
)


# make sure 출산율 is numeric and drop NA
df['출산율'] = pd.to_numeric(df['출산율'], errors='coerce')
df = df.dropna(subset=['출산율']).reset_index(drop=True)

# check values in SIGUNGU_NM from geo_data and 행정구역 from df match
geo_data = geo_data[geo_data['SIGUNGU_NM'].isin(df['행정구역'])]
df = df[df['행정구역'].isin(geo_data['SIGUNGU_NM'])]

# reset index
geo_data = geo_data.reset_index(drop=True)
df = df.reset_index(drop=True)

# create a separate index column to join two dataframes later on
geo_data['index'] = geo_data.index
df['index'] = df.index

# title
title = '한국 출산율'
title_html = f'<h3 align="center" style="font-size:20px"><b>{title}</b></h3>'

# seoul city hall coordinates
city_hall = [37.5665, 126.9780]

# folium map 
gu_map = folium.Map(location=city_hall, 
                    zoom_start=8,
                    tiles='cartodbpositron')

gu_map.get_root().html.add_child(folium.Element(title_html))

# create Choropleth map using 'index' as key
folium.Choropleth(
    geo_data=geo_data,
    data=df,
    columns=('index', '출산율'),
    key_on='feature.properties.index',
    fill_color='BuPu',
    fill_opacity=0.7,
    line_opacity=0.5,
    legend_name='출산율'
).add_to(gu_map)

# create 출산율 column for geo_data 
geo_data['출산율'] = df['출산율']

# add tooltips using GeoJsonTooltip
folium.GeoJson(
    geo_data,
    style_function=lambda x: {
        'fillColor': '#ffffff00', 'color': 'black', 'weight': 0.5, 'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['SIGUNGU_NM', '출산율'],
        aliases=['행정구역: ', '출산율: '],
        localize=True,
        sticky=False
    )
).add_to(gu_map)


# Streamlit application
st.title("한국 출산율 지도")

folium_static(gu_map)

# display dataFrame
st.subheader("출산율 데이터")
st.dataframe(df.iloc[:,0:2])  # Use st.table(df) if you prefer a static table view