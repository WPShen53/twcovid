import pandas
from statsmodels.tsa.arima.model import ARIMA

def fit_model (series, lag=8):
    series.dropna(inplace=True)

    model = ARIMA(series.asfreq('d'),order=(lag,1,0))
    model_fit = model.fit()

    return model, model_fit