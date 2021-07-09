import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

# from app import app
from apps import daily_chart, model_pred, data_update

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if (pathname == '/apps/daily_chart' or pathname =='/'):
        return daily_chart.layout
    elif pathname == '/apps/model_pred':
        return model_pred.layout
    elif pathname == '/apps/data_update':
        return data_update.layout
    else:
        return '404 {}',format(pathname)

if __name__ == '__main__':
    app.run_server(debug=True)