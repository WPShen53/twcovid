import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import timedelta

def plot_confirm_case (df):
    fig = px.line(df, y=['Original', 'Corrected', '7d Rolling'])
    return fig

def plot_death_case (df):
    fig = px.line(df, y=['Death'])
    return fig

def plot_df (df, labels=[]):
    if (len(labels)==0): labels = df.columns
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    for label in labels:
        if label == "dead":
            fig.add_trace(go.Scatter(x=df.index, y=df[label], mode='lines', name=label), secondary_y=True)
            fig.update_yaxes(title_text='Daily Death Cases',secondary_y=True)
        else:
            fig.add_trace(go.Scatter(x=df.index, y=df[label], mode='lines', name=label), secondary_y=False)
    fig.update_layout(title='TW Covid-19 CDC Daily Announcement', xaxis_title='Date')
    fig.update_yaxes(title_text='Daily Positive Cases',secondary_y=False)
    return fig

def plot_model_prediction (series, model_fit, lag=8):
    fct = {}
    validate_period = lag * 2
    fct_range = series.tail(n=validate_period).index
    for sdate in fct_range:
        fct[sdate] = model_fit.predict(start=sdate,end=sdate+timedelta(days=1),dynamic=True)[0]
    fcts = pd.Series(fct)
    pred = model_fit.predict(start=sdate,end=sdate+timedelta(days=lag),dynamic=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series.to_list(), mode='lines', name=series.name))
    fig.add_trace(go.Scatter(x=fcts.index, y=fcts.to_list(), mode='lines', name='Validation'))
    fig.add_trace(go.Scatter(x=pred.index, y=pred.to_list(), name='Prediction', line=dict(color='royalblue', dash='dash')))
    fig.update_layout(title='TW Covid-19 Case with ARIMA Prediction',
                   xaxis_title='Date',
                   yaxis_title='Daily Positive Cases')
    return fig