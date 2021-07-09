import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from twc import tcdata, tcplot, tcmodel

from app import app

columns = ['Original','Corrected','7d Rolling','dead']


layout = html.Div (children=[
    html.Div(html.H4(children='TW CDC Daily News Conference Announcements')),
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
    html.Div(
        children=[dcc.Graph(id="line-chart")],
        style={'width': '78%', 'display': 'inline-block'}
    ),
    html.Br(),
    dcc.Link('Go to Model Chart', href='/apps/model_pred'),
    html.Br(),
    dcc.Link('Go to Data Page', href='/apps/data_update')
])


@app.callback(
    Output("line-chart", "figure"), 
    [Input("checklist", "value")])
def display_value(options):
    df = tcdata.get_twcovid_df_from_db()
    fig = tcplot.plot_df(df, options)   
    return fig