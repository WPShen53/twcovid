from statsmodels.tsa.arima.model import ARIMA

def fit_ARIMA_model (series, lag=8):
    series.dropna(inplace=True)

    model = ARIMA(series.asfreq('d'),order=(lag,1,0))
    model_fit = model.fit()

    return model_fit