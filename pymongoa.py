import json, os, pprint
import pymongo

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta

sns.set(rc={"figure.figsize":(11, 5)})
def date_formater(ax):
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

db_client = pymongo.MongoClient("mongodb://localhost:27017")
# print(db_client.list_database_names())
for db in db_client.list_databases(): 
    pprint.pprint(db)
covid_db = db_client["tw_covid"]
for col in covid_db.list_collections(): 
    pprint.pprint(col)
documents = covid_db["daily.announcement"]

## Insert document from json files
documents.delete_many({})
directory = "./data/"
for filename in os.listdir(directory):
    with open(directory+filename) as f: file_data = json.load(f)
    if isinstance(file_data, dict): 
        documents.insert_one(file_data)
    else : 
        documents.insert_many(file_data)

## Delete documents
# documents.delete_one({"date":"2020-01-01"})

## Get death trend
death = {}
days = []
records = documents.find({"dead":{"$exists":True}}, {"_id":0, "date":1, "dead":1}).sort("date", 1)
for x in records: 
    death[x["date"]]=int(x["dead"])
df_death = pd.DataFrame.from_dict(death, orient="index")
df_death.index = pd.to_datetime(df_death.index)
df_death.rename(columns={0:"dead"}, inplace=True)
ax = df_death.plot()
date_formater(ax)
plt.show()

## Find the Original(Min) and Corrected(Max) case number of a date
daily_amt = {}
for x in documents.find({}):
    val = []
    searchDate = x["date"]
    init_val = documents.find_one({"date": searchDate},{"_id":0,"cases":1})
    if (init_val != None):
        val.append(int(init_val["cases"]))
    records = documents.find({"corrections.date": searchDate}, {"_id":0, "date":1, "corrections.cases.$":1}).sort("date", 1)
    for _i, x in enumerate(records):
        val.append(int(x["corrections"][0]["cases"]))
    daily_amt[searchDate] = {"Original":min(val), "Corrected":max(val), "Updates":len(val)}
df_daily = pd.DataFrame.from_dict(daily_amt, orient="index")
df_daily.index = pd.to_datetime(df_daily.index)
df_daily.index.rename('date', inplace=True)
df_daily["7d Rolling"] = df_daily["Corrected"].rolling(7, center=True).mean()
df_daily["dead"] = df_death

df_daily.to_csv("dailyDF.csv")
db_client.close()

## if there is no MongoDB for the data, load the dataframe from csv
# df_daily = pd.read_csv("dailyDF.csv", index_col="date")
# df_daily.index = pd.to_datetime(df_daily.index)
pprint.pprint(df_daily)
ax = df_daily[["Original","Corrected","7d Rolling"]].plot(stacked=False)
plt.show()

## Modeling and Forecasting
## Using Autocorrelation and ARIMA parameters for forecast
series = df_daily["7d Rolling"]
series.dropna(inplace=True)

# use autocorrelation to find the legs of time series
ax = pd.plotting.autocorrelation_plot(series)
ax.grid('on', which='major', axis='x' )
plt.show()
lag = 8

model=ARIMA(series.asfreq('d'),order=(lag,1,0))
model_fit=model.fit()
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
print('\n<== Residual Description ==>')
print(residuals.describe())

# forecast with the single ARIMA model, fit(8,1,0)
fct = {}
validate_period = 15
fct_range = series.tail(n=validate_period).index
for sdate in fct_range:
    fct[sdate] = model_fit.predict(start=sdate,end=sdate+timedelta(days=1),dynamic=True)[0]
fcts = pd.Series(fct)
# evaluate forecasts
rmse = sqrt(mean_squared_error(series.tail(n=validate_period), fcts)) 
print('\n<== Model Validation ==> RMSE: %.3f' % rmse)

## Plot chat
fig, ax = plt.subplots(constrained_layout=True)
date_formater(ax)
ax.plot(series, label= '7d rolling average')
ax.plot(fcts, 'r' , label="validation")
pred = model_fit.predict(start=sdate,end=sdate+timedelta(days=lag),dynamic=True)
ax.plot(pred, '--r' , label=sdate.strftime("%x")+" prediction")
plt.xlabel("date")
plt.ylabel("positive cases")
plt.legend(framealpha=1, frameon=True)
plt.show()