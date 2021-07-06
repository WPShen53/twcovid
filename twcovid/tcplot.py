import matplotlib.pyplot as plt
import plotly.express as px

def plot_confirm_case (df):
    fig = px.line(df, y=['Original', 'Corrected', '7d Rolling'])
    return fig

def plot_death_case (df):
    fig = px.line(df, y=['Death'])
    return fig

def plot_df (df, labels=[]):
    if (len(labels)==0): labels = df.columns
    fig = px.line(df, y=labels)
    return fig