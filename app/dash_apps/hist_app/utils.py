import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def histplot(min:int, max:int, city:str, df):
    temp = df.loc[
        (df.index == city) &
        (df['interest'] <= max) &
        (df['interest'] >= min)
    ].copy()
    
    temp = temp.groupby('category')['count'].agg('sum').to_frame()

    fig = px.bar(
        x=temp.index, 
        y=temp['count'], 
        labels={'x':'Price', 'y':'Sales Volume'}
        )
    fig.update_layout(
        title=f"Price distribution in {city.lower().capitalize()}, France for interest rates between {min}% and {max}% (2015-2023)",
        xaxis={
            'title': 'Price (in €)', 'range': [0, 1000000],
            'tickmode': 'array',
            'tickvals': [i for i in range(0, 1000000, 100000)],
            'ticktext': ['0'] + [str(int(i/1000))+'k' for i in range(100000, 1000000, 100000)]
            },
        yaxis={'title': 'Sale Volumes'},
        barmode='relative',
        bargap=0
    )
    return fig, temp

def analyze_graph(city:str, df):
    _, temp1 = histplot(1.0, 1.5, city, df)
    _, temp2 = histplot(2.5, 3.0, city, df)
    tot1 = temp1['count'].sum(axis=0)
    tot2 = temp2['count'].sum(axis=0)
    temp1 = temp1.apply(lambda x: x['count']/tot1, axis=1)
    temp2 = temp2.apply(lambda x: x['count']/tot2, axis=1)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(
        x=temp1.index,
        y=temp1.values,
        name='1.0%-1.5%',
        marker=dict(
            color='rgb(34,163,192)'
                ),
        line_shape='spline',
        line_smoothing=1.0
        ))


    fig.add_trace(go.Scatter(
        x=temp2.index,
        y=temp2.values,
        name='2.5%-3.0%',
        yaxis='y2',
        line_shape='spline',
        line_smoothing=1.0
    ),secondary_y=False)

    fig.update_layout(
        title=f"Price distribution for high vs. low Interest Rates in {city.lower().capitalize()}, France. (2015-2024)",
        xaxis={
            'title': 'Price (in €)',
            'range': [0, 1000000],
            'tickmode': 'array',
            'tickvals': [i for i in range(0, 1000000, 100000)],
            'ticktext': ['0'] + [str(int(i/1000))+'k' for i in range(100000, 1000000, 100000)]
            },
        yaxis={
            'tickformat': '.0%'
        }
    )

    return fig


def graph_geo(df, year, departements):
    fig = px.choropleth(
        data_frame=df.loc[f'{year}-12-31'],
        locations='deps',
        geojson=departements,
        color='pps',
        scope='europe',
        labels={
            'pps': 'Price per square meter (in €)'
        }
    )

    fig.update_geos(
        fitbounds='locations', visible=False
    )

    fig.update_layout(
        #width=600,
        title='Price per square meter (€/m²) per departement in France since 2015',
    )

    return fig