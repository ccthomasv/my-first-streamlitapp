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

# import geodata
with open("./data/georef-switzerland-kanton.geojson") as response:
    geo_data = json.load(response)

# data wrangling
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

# pivot tables
df4_elect_cap_pivot = pd.pivot_table(df4, index='canton_name', values = 'electrical_capacity', aggfunc='sum')
df4_prod_pivot = pd.pivot_table(df4, index='canton_name', values = 'production', aggfunc='sum')
df4_tariff_pivot = pd.pivot_table(df4, index='canton_name', values = 'tariff', aggfunc='sum')

# Add title and header
st.title("Renewable Power Plants in Switzerland")
st.header("Electrical capacity | Production | Tariff by cantons")
url = 'https://open-power-system-data.org/'
st.write('Data Source:', url)

# page layout
left_column, middle_column, right_column = st.columns([2, 1, 1])

# Widgets: checkbox for dataset sample
if st.checkbox("Show Dataframe"):
    st.subheader('This is the dataset sample:')
    st.dataframe(data=df4.head())

# Widgets: selectbox for maps
maps = ["Installed Electrical Capacity"]+["Yearly Production"]+["Tariff"]
map = left_column.selectbox("Choose a map type", maps)

# Widgets: radio buttons
show_scatt = middle_column.radio(
    label='Show Scatter Plot', options=['Yes', 'No'])

# Flow control and plotting (maps)
if map == "Installed Electrical Capacity":
    fig4_pivot = df4_elect_cap_pivot
    map_color = 'electrical_capacity'
    map_colorscale = 'Electric'
    map_colorrange = [0, 185]

elif map == "Yearly Production":
    fig4_pivot = df4_prod_pivot
    map_color = 'production'
    map_colorscale = 'Blackbody'
    map_colorrange = [0, 450000]

elif map == "Tariff": 
    fig4_pivot = df4_tariff_pivot
    map_color = 'tariff'
    map_colorscale = 'Hot'
    map_colorrange = [1000000, 90000000]

# Scatter: Production vs Tariff
fig5 = go.Figure()
cantons = df4['canton_name'].unique()
df4_tariff = df4[['tariff', 'production', 'electrical_capacity', 'canton_name']].groupby(['canton_name']).agg('sum').reset_index()
for canton in cantons:
    df4_aux = df4_tariff[df4_tariff['canton_name']==canton]
    fig5.add_traces(
        go.Scatter(
            x=df4_aux['tariff'], y=df4_aux['production'], 
            mode="markers", 
            name=canton, showlegend=False ,
            marker={"size": df4_aux['electrical_capacity'], 'symbol': 'hexagon',
                    "sizeref": 2.5, "sizemode": "diameter"},
            text=df4_aux['canton_name'],
            hovertemplate="<b>%{text}</b><br><br>" +
                "Yearly Production (MWh): %{y:,.0f}<br>" +
                "Tariff for 2016: %{x:$,.0f}<br>" +
                "Electrical Capacity (MW): %{marker.size:,}" +
                "<extra></extra>"
        )
    )
fig5.update_layout(
    title={"text": "Renewable Power Plants Production vs Tariff in Swiss (2016)", "font": {"size": 24}},
    xaxis={"title": {"text": "Tariff for 2016 (CHF)", "font": {"size": 16}}},
    yaxis={"title": {"text": "Yearly Production (MWh)", "font": {"size": 16}}},
)

# Flow control and plotting (scatter)
if show_scatt == "Yes":
    st.plotly_chart(fig5)


# map: electrical capacity
fig4 = px.choropleth_mapbox(fig4_pivot, geojson=geo_data, color=fig4_pivot[map_color],
                           locations=fig4_pivot.index.values, featureidkey="properties.kan_name", 
                           color_continuous_scale=map_colorscale, range_color=map_colorrange, 
                           hover_name=fig4_pivot.index.values)

fig4.update_layout(mapbox_style="carto-positron",
                   mapbox_zoom=6, mapbox_center = {"lat": 46.8182, "lon": 8.2275})
                   
fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig4)

# st.balloons()

# map: production
# fig42 = px.choropleth_mapbox(df4_prod_pivot, geojson=geo_data, color=df4_prod_pivot['production'],
#                            locations=df4_prod_pivot.index.values, featureidkey="properties.kan_name", 
#                            color_continuous_scale='Blackbody', range_color=[0, 450000], 
#                            hover_name=df4_prod_pivot.index.values)

# fig42.update_layout(mapbox_style="carto-positron",
#                    mapbox_zoom=6.5, mapbox_center = {"lat": 46.8182, "lon": 8.2275})
                   
# fig42.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# # map: tariff
# fig43 = px.choropleth_mapbox(df4_tariff_pivot, geojson=geo_data, color=df4_tariff_pivot['tariff'],
#                            locations=df4_tariff_pivot.index.values, featureidkey="properties.kan_name", 
#                            color_continuous_scale='Hot', range_color=[1000000, 90000000], 
#                            hover_name=df4_tariff_pivot.index.values)

# fig43.update_layout(mapbox_style="carto-positron",
#                    mapbox_zoom=6.5, mapbox_center = {"lat": 46.8182, "lon": 8.2275})
                   
# fig43.update_layout(margin={"r":0,"t":0,"l":0,"b":0})