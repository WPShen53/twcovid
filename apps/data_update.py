import dash_core_components as dcc
import dash_html_components as html
import dash_table
import config
from dash.dependencies import Input, Output
from twc import tcdata
from app import app

display_columns = ['date','Original','Corrected','7d Rolling','dead']

# format for Dash Table to display
def format_df (df):
    dff = df.reset_index()
    dff['date'] = dff['date'].dt.date
    dff.fillna(value=0, inplace=True)
    dff['7d Rolling'] = dff['7d Rolling'].round()
    return dff.to_dict('records')


layout = html.Div(children=[
    html.Div([
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
    ),
    html.Br(),
    dcc.Link('Go to Daily Chart', href='/apps/daily_chart'),
    html.Br(),
    dcc.Link('Go to Model Prediction', href='/apps/model_pred')
])

@app.callback( 
    Output("refresh-result", "children"),
    Output("table", "data"),
    [Input("data-refresh", "n_clicks")]
    )
def refresh_data_update_model_chart (n_clicks):
    if (n_clicks != 0):
        if (config.use_DB == True): 
            tcdata.refresh_data_from_json(dir=config.data_dir)
            msg = 'OK, Data refreshed from json to MongoDB, click {} times'.format(n_clicks)
        else:
            msg = 'Use DB is {}. Load internal data'.format(config.use_DB)
    else:
        msg = ''
    df = tcdata.get_twcovid_df(from_DB=config.use_DB, db_str=config.db_str)
    data = format_df(df)
    return msg, data