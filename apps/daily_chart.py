import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from twc import tcdata, tcplot
from app import app
import config

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
    dcc.Link('Go to Model Predction', href='/apps/model_pred'),
    html.Br(),
    dcc.Link('Go to Data Update', href='/apps/data_update')
])


@app.callback(
    Output("line-chart", "figure"), 
    [Input("checklist", "value")])
def display_value(options):
    df = tcdata.get_twcovid_df(from_db=config.use_db, db_str=config.db_str)
    fig = tcplot.plot_df(df, options)   
    return fig