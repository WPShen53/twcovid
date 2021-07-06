# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
import twcovid.tcdata as tcdata, twcovid.tcplot as tcplot

df = tcdata.get_twcovid_df_from_db()
columns = df.columns

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div([
    dcc.Checklist(
        id="checklist",
        options=[{"label": x, "value": x} for x in columns],
        value=columns,
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id="line-chart"),
])

@app.callback( 
    Output("line-chart", "figure"), 
    [Input("checklist", "value")]
    )

def update_line_chart(options):
    fig = tcplot.plot_df(df, options)
    return fig


# app.layout = html.Div(children=[
#     html.H1(children='Hello Dash'),
#     html.Div(children='''
#         Dash: A web application framework for Python.
#     '''),
#     dcc.Graph(
#         id='example-graph',
#         figure=fig
#     )
# ])

if __name__ == '__main__':
    app.run_server(debug=True)