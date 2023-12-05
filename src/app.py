import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# cache data
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

# load data
df4_raw = load_data(path='./data/renewable_power_plants_CH.csv')
df4 = deepcopy(df4_raw)
df4['canton_name'] = df4['canton']

st.balloons()

# Add title and header
st.title("Renewable Power Plants in Switzerland")
st.header("Electrical capacity by cantons")
url = 'https://open-power-system-data.org/'
st.write('Data Source:', url)

# page layout
left_column, middle_column, right_column = st.columns([3, 1, 1])



if st.sidebar.checkbox("Show Dataframe"):
    st.subheader('This is my dataset:')
    st.dataframe(data=df4.head())

with open("./data/georef-switzerland-kanton.geojson") as response:
    geo_data = json.load(response)

cantons_dict = {'TG':'Thurgau', 
                'GR':'Graubünden', 
                'LU':'Luzern', 
                'BE':'Bern', 
                'VS':'Valais', 
                'BL':'Basel-Landschaft', 
                'SO':'Solothurn', 
                'VD':'Vaud', 
                'SH':'Schaffhausen', 
                'ZH':'Zürich', 
                'AG':'Aargau', 
                'UR':'Uri', 
                'NE':'Neuchâtel', 
                'TI':'Ticino', 
                'SG':'St. Gallen', 
                'GE':'Genève', 
                'GL':'Glarus', 
                'JU':'Jura', 
                'ZG':'Zug', 
                'OW':'Obwalden', 
                'FR':'Fribourg', 
                'SZ':'Schwyz', 
                'AR':'Appenzell Ausserrhoden', 
                'AI':'Appenzell Innerrhoden', 
                'NW':'Nidwalden', 
                'BS':'Basel-Stadt'}

df4 = df4.replace({"canton_name": cantons_dict})

df4_elect_cap_pivot = pd.pivot_table(df4, index='canton_name', values = 'electrical_capacity', aggfunc='sum')

fig4 = px.choropleth_mapbox(df4_elect_cap_pivot, geojson=geo_data, color=df4_elect_cap_pivot['electrical_capacity'],
                           locations=df4_elect_cap_pivot.index.values, featureidkey="properties.kan_name", 
                           color_continuous_scale='Electric', range_color=[0, 185], 
                           hover_name=df4_elect_cap_pivot.index.values)

fig4.update_layout(mapbox_style="carto-positron",
                   mapbox_zoom=6.5, mapbox_center = {"lat": 46.8182, "lon": 8.2275})
                   
fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig4)