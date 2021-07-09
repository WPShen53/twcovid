import dash_core_components as dcc
import dash_html_components as html
from twc import tcdata, tcmodel, tcplot

from app import app

df = tcdata.get_twcovid_df_from_db()
series = df['7d Rolling']
model_fit = tcmodel.fit_ARIMA_model(series)
fig = tcplot.plot_model_prediction(series, model_fit) 


layout = html.Div([

    html.Div(html.H4(children='Model Validation & Prediction')),
    html.Div(
        children=[dcc.Graph(id='model-graph', figure=fig)],
        style={'width': '78%', 'display': 'inline-block'}
    ),
    
    html.Br(),
    dcc.Link('Go to Daily Chart', href='/apps/daily_chart'),
    html.Br(),
    dcc.Link('Go to Data Page', href='/apps/data_update')
])
