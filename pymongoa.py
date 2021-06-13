import pandas as pd
import matplotlib.pyplot as plt, matplotlib.dates as mdates
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA
import pymongo
import json, os, pprint

dbclient = pymongo.MongoClient("mongodb://localhost:27017")
print(dbclient.list_database_names())
for db in dbclient.list_databases(): pprint.pprint(db)

coviddb = dbclient["tw_covid"]
for col in coviddb.list_collections(): pprint.pprint(col)

col_da = coviddb["daily.announcement"]
pprint.pprint(col_da.find_one())

## Insert document from json files
col_da.delete_many({})
directory = "./data/"
for filename in os.listdir(directory):
    print(filename)
    with open(directory+filename) as f: file_data = json.load(f)
    if isinstance(file_data, dict): col_da.insert_one(file_data)
    else : col_da.insert_many(file_data)

## Delete documents
# col_da.delete_one({"date":"2020-01-01"})

## Get death trend
death = {}
days = []
records = col_da.find({"dead":{"$exists":True}}, {"_id":0, "date":1, "dead":1}).sort("date", -1)
for x in records: 
    death[x["date"]]=x["dead"]
pprint.pprint(death)
df_death = pd.DataFrame.from_dict(death, orient="index")
df_death.index = pd.to_datetime(df_death.index)
df_death.rename(columns={0:"dead"}, inplace=True)
df_death.plot()
# df_death.plot.barh()
plt.show()

## Find Min/Max of a date
dailyAmt = {}
for x in col_da.find({}):
    val = []
    searchDate = x["date"]
    init_val = col_da.find_one({"date": searchDate},{"_id":0,"cases":1})
    if (init_val != None):
        val.append(int(init_val["cases"]))
    records = col_da.find({"corrections.date": searchDate}, {"_id":0, "date":1, "corrections.cases.$":1}).sort("date", 1)
    for _i, x in enumerate(records):
        val.append(int(x["corrections"][0]["cases"]))
    dailyAmt[searchDate] = {"Min":min(val), "Max":max(val)}
# pprint.pprint(dailyAmt)
df_daily = pd.DataFrame.from_dict(dailyAmt, orient="index")
df_daily["7d Rolling"] = df_daily["Max"].rolling(7).mean()
df_daily.index = pd.to_datetime(df_daily.index)
pprint.pprint(df_daily)

sns.set(rc={"figure.figsize":(11, 5)})
ax = df_daily.plot(stacked=False)
plt.show()

dbclient.close()


## Using Autocorrelation and ARIMA parameters for forecast
series = df_daily["7d Rolling"]
series.dropna(inplace=True)

# use autocorrelation to fine the legs of time series
pd.plotting.autocorrelation_plot(series)
plt.show()
model=ARIMA(series.asfreq('d'),order=(5,1,0))
model_fit=model.fit()
# summary of fit model
# print(model_fit.summary())

# line plot of residuals
residuals = pd.DataFrame(model_fit.resid)
ax = residuals.plot()
ax.grid('on', which='major', axis='y' )
plt.show()
# density plot of residuals, check if is center around 0
ax = residuals.plot(kind='kde')
ax.grid('on', which='major', axis='x' )
plt.show()
# summary stats of residuals
print(residuals.describe())

# forecast
fct = model_fit.predict(start="2021-06-13",end="2021-06-20",dynamic=True)
fig, ax = plt.subplots(constrained_layout=True)
locator = mdates.AutoDateLocator()
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.plot(series, label= '7d rolling average')
ax.plot(fct, '--r' , label="forecast")
plt.xlabel("date")
plt.ylabel("positive cases")
plt.legend(framealpha=1, frameon=True)
plt.show()


from sklearn.metrics import mean_squared_error
from math import sqrt
# split into train and test sets
X = series.values
size = int(len(X) * 0.66)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
# walk-forward validation
for t in range(len(test)):
	model = ARIMA(history, order=(5,1,0))
	model_fit = model.fit()
	output = model_fit.forecast()
	yhat = output[0]
	predictions.append(yhat)
	obs = test[t]
	history.append(obs)
	print('predicted=%f, expected=%f' % (yhat, obs))
# evaluate forecasts
rmse = sqrt(mean_squared_error(test, predictions))
print('Test RMSE: %.3f' % rmse)
# plot forecasts against actual outcomes
plt.plot(test, label= "expected")
plt.plot(predictions, '--r' , label="predicted")
plt.legend(framealpha=1, frameon=True)
plt.show()

