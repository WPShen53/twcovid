# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from twc import tcdata, tcplot, tcmodel

columns = ['Original','Corrected','7d Rolling','dead']
display_columns = ['date','Original','Corrected','7d Rolling','dead']

# format for Dash Table to display
def format_df (df):
    dff = df.reset_index()
    dff['date'] = dff['date'].dt.date
    dff.fillna(value=0, inplace=True)
    dff['7d Rolling'] = dff['7d Rolling'].round()
    return dff.to_dict('records')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# see https://plotly.com/python/px-arguments/ for more options

app.layout = html.Div (children=[
    html.Div(html.H4(children='TW CDC Daily News Conference Announcements')),
    html.Div(
        children=[dcc.Graph(id="line-chart")],
        style={'width': '78%', 'display': 'inline-block'}
    ),
    
    html.Div(
        children=[
            dcc.Checklist(
                id="checklist",
                options=[{"label": x, "value": x} for x in columns],
                value=columns
            )
        ],
        style={'width': '18%', 'float': 'right','display': 'inline-block'}
    ),


    html.Div(html.H4(children='Model Validation & Prediction')),
    html.Div(
        children=[dcc.Graph(id='model-graph')],
        style={'width': '78%', 'display': 'inline-block'}
    ),

    html.Div(
        children=[
            html.H4(children='TW Covid Case Dataset'),
            html.Button('Refresh Data', id='data-refresh', n_clicks=0),
            html.Div(id='refresh-result'),
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in display_columns],
                style_as_list_view=True,
                style_cell={'textAlign': 'center'},
                style_header={ 'fontWeight': 'bold', 'border': '1px solid black' },
                style_cell_conditional=[
                    { 'if': {'column_id': 'date'}, 'textAlign': 'center' },
                ],
                page_size=10
            )
        ],
        style={'width': '40%', 'display': 'inline-block', 'fontSize': 14}
    )
])

@app.callback( 
    Output("model-graph", "figure"), 
    Output("line-chart", "figure"), 
    Output("refresh-result", "children"),
    Output("table", "data"),
    [Input("data-refresh", "n_clicks"),Input("checklist", "value")]
    )
def refresh_data_update_model_chart (n_clicks, options):
    if (n_clicks != 0): 
        tcdata.refresh_data_from_json(dir="./data/")
        msg = 'OK, Data Refreshed, click {} times'.format(n_clicks)
    else:
        msg = ''
    df = tcdata.get_twcovid_df(from_DB = True, db_str="mongodb://localhost:27017")
#    df = tcdata.get_twcovid_df(from_DB = False)
    data = format_df(df)
    series = df['7d Rolling']
    model_fit = tcmodel.fit_ARIMA_model(series)
    fig1 = tcplot.plot_model_prediction(series, model_fit) 
    fig2 = tcplot.plot_df(df, options)   
    return fig1, fig2, msg, data

if __name__ == '__main__':
    app.run_server(debug=True)