import tcdata, tcplot, tcmodel
import pprint

tcdata.refresh_data_from_json()
df = tcdata.get_twcovid_df_from_db()
pprint.pprint(df)

fig = tcplot.plot_confirm_case(df)
fig.show()

series = df['7d Rolling']
model_fit = tcmodel.fit_ARIMA_model(series)
print(model_fit.summary())

fig = tcplot.plot_model_prediction(series, model_fit)
fig.show()