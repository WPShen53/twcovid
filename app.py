# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from twc import tcdata, tcplot, tcmodel

df = tcdata.get_twcovid_df_from_db()
dff = df.reset_index()
columns = df.columns
series = df['7d Rolling']
model, model_fit = tcmodel.fit_model(series)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div (children=[
    html.Div(children=[
        html.H4(children='TW CDC Daily News Conference Announcements'),
        dcc.Checklist(
            id="checklist",
            options=[{"label": x, "value": x} for x in columns],
            value=columns,
            labelStyle={'display': 'inline-block'}
        ),
        dcc.Graph(id="line-chart")
    ]),

    html.Div(children=[
        html.H4(children='Model Validation & Prediction'),
        dcc.Graph(
            id='model-graph',
            figure=tcplot.plot_model_prediction(series, model_fit)
        )
    ]),

    html.Div(children=[
        html.H4(children='TW Covid Case Dataset'),
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in dff.columns],
            data=dff.to_dict('records'),
            page_size=10
        )
    ])

])

@app.callback( 
    Output("line-chart", "figure"), 
    [Input("checklist", "value")]
    )
def update_line_chart(options):
    fig = tcplot.plot_df(df, options)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)