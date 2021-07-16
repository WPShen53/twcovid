from twc import tcdata, tcplot, tcmodel
import config
import pprint

if (config.use_db == True):
    tcdata.refresh_data_from_json(dir=config.data_dir)
df = tcdata.get_twcovid_df(from_db=config.use_db, db_str=config.db_str)
pprint.pprint(df)

fig = tcplot.plot_confirm_case(df)
fig.show()

fig = tcplot.plot_df(df)
fig.show()

series = df['7d Rolling']
model_fit = tcmodel.fit_ARIMA_model(series)
print(model_fit.summary())

fig = tcplot.plot_model_prediction(series, model_fit)
fig.show() 