import tcdata, tcplot, tcmodel
import pprint

# tcdata.refresh_data_from_json(dir = './data/')
# df = tcdata.get_twcovid_df(from_DB = True, db_str="mongodb://localhost:27017")
df = tcdata.get_twcovid_df(from_DB = False)
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