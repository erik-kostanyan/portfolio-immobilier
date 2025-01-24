from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
from django_plotly_dash import DjangoDash

import plotly.express as px
import plotly.graph_objects as go

import sqlite3
import os
import json
from pathlib import Path
import pandas as pd

from .utils import histplot, analyze_graph, graph_geo

# Root folder to navigate easily
BASE_FOL = Path(__name__).resolve().parent

# The headers that will serve as column names in the dataframes
header_hist = ['ville', 'interest', 'category', 'count']
header_geo = ['date_transaction', 'departement', 'pps', 'count', 'deps']

# Geojson file that will be used to plot the map graph
with open(os.path.join(BASE_FOL, 'app/dash_apps/hist_app/france_departements.json'), 'r') as f:
    departements = json.load(f)

# Add 'id' to the geojson dict; this is used by plotly to map to the dataframe
for feature in departements['features']:
    feature['id'] = feature['properties']['code']

# Custom function to populate dataframes by querying the sqlite3 database in root
def query_to_db(ville:str):
    cnx = sqlite3.connect(os.path.join(BASE_FOL, 'db.sqlite3'))
    cursor = cnx.cursor()
    cursor.execute(f'SELECT * FROM france_immobilier WHERE ville="{ville}"')
    df = pd.DataFrame(data=cursor.fetchall(), columns=header_hist)
    df = df.set_index(['ville'])
    return df

def query_to_geo():
    cnx = sqlite3.connect(os.path.join(BASE_FOL, 'db.sqlite3'))
    cursor = cnx.cursor()
    cursor.execute(f'SELECT * FROM france_geo')
    df_geo = pd.DataFrame(data=cursor.fetchall(), columns=header_geo)
    df_geo.set_index(['date_transaction', 'departement'], inplace=True)
    return df_geo

# Populate the df dataframe with some starting data
df = query_to_db('CANNES')
df_geo = query_to_geo()

# Retrieve list with all distinct city names is France
cnx = sqlite3.connect(os.path.join(BASE_FOL, 'db.sqlite3'))
cursor = cnx.cursor()
cursor.execute("SELECT DISTINCT ville FROM france_immobilier")
cities = cursor.fetchall()
cities = [c[0] for c in cities]


# Create the app
app = DjangoDash('immo_dashboard_dash', external_stylesheets=[dbc.themes.BOOTSTRAP])
app.css.append_css({"external_url" : "/static/styles/override.css" })

app.layout = html.Div(children=[
    html.Div(id='div-app', className='div-app', children=[
        dbc.Container([
            html.Div(className='card div-b', children=[
                html.Div(className='card-body', children=[
                    html.H5(html.B('French Real Estate'), className='card-title'),
                    html.P('Please select a city from the dropdown menu below.'),
                    html.P('You can use the slider to determine the range of the interest rates to get a view of the subsequent results.'),
                ]),
            ]),
            dbc.Row([
                dropdown := dcc.Dropdown(cities, value='CANNES'),
                html.Br(),
                html.P('Interest Rate Range:'),
                slider := dcc.RangeSlider(0.0, 3.5, value=[1.0, 1.5])
            ]),
            dbc.Row([
                dbc.Col([
                    dls.Hash(
                        gr := dcc.Graph(figure={}),
                        color="#435278",
                        speed_multiplier=2,
                        size=100,
                        id='main_hash'
                    )
                ], width=12)
            ]),
            html.Br(), 
            html.Br(), 
            dbc.Row([
                dbc.Col([
                    dls.Hash(
                        gr_analyze := dcc.Graph(figure={}),
                        color="#435278",
                        speed_multiplier=2,
                        size=100,
                        id='analyze_hash'
                    )
                ], width=12)
            ]),
            html.Br(), 
            html.Br(), 
            html.Div(className='card div-b', children=[
                html.Div(className='card-body', children=[
                    html.H5(html.B('Average price per meter squared per departement in France'), className='card-title'),
                    html.P('Please select a specific year with the slider on the bottom.'),
                ]),
            ]),
            dbc.Row([
                dbc.Col([
                    dls.Hash(
                        gr_geo := dcc.Graph(figure={}),
                        color="#435278",
                        speed_multiplier=2,
                        size=100,
                        id='geo_hash'
                    )
                ], width=12)
            ]),
            geo_slider := dcc.Slider(
                min=2015, 
                max=2023, 
                step=1, 
                value=2023, 
                marks={i: '{}'.format(i) for i in range(2015,2023,1)}
            )
        ])
    ])
])
###############################################################################################################################

@app.callback(
    Output(slider, 'value'),
    Input(dropdown, 'value')
)
def update_graph(city):
    return [1.0, 1.5]

@app.callback(
    Output(gr, component_property='figure'),
    Input(dropdown, 'value'),
    Input(slider, 'value')
)
def update_graph(city, slider):
    if city is None:
        return go.Figure(data=None)

    else:
        global df
        if df.index.get_level_values('ville')[0] != city:
            df = query_to_db(city)
        try:
            fig, _ = histplot(slider[0], slider[1], city, df)
            return fig
        except Exception as error:
            print(f'update_graph: {error}')
            return go.Figure(data=None)

@app.callback(
    Output(gr_analyze, component_property='figure'), 
    Input(dropdown, 'value')
)
def Analyse(city):
    if city is None:
        return go.Figure(data=None)
    else:
        global df
        if df.index.get_level_values('ville')[0]!= city:
            df = query_to_db(city)
        try:
            # Call the 'plot_analyzer' to return a dataframe
            return analyze_graph(city, df)
        except Exception as error: 
            print(f'Analyse: {error}')
            return go.Figure(data=None)    
    
@app.callback(
    Output(gr_geo, component_property='figure'),
    Input(geo_slider, 'value'),
    Input(dropdown, 'value')
)
def geo(year, city):
    if city is None:
        return go.Figure(data=None)
    else:
        global df
        if df.index.get_level_values('ville')[0] != city:
            df = query_to_db(city)
        try:
            global df_geo
            global departements
            return graph_geo(df_geo, year, departements)
        except Exception as error:
            print(f'GEO:{error}')
            return go.Figure(data=None)