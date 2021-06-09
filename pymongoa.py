import pandas as pd
import matplotlib.pyplot as plt
import pymongo
import json, os
import pprint

dbclient = pymongo.MongoClient("mongodb://localhost:27017")
print(dbclient.list_database_names())
for db in dbclient.list_databases(): pprint.pprint(db)

coviddb = dbclient["tw_covid"]
for col in coviddb.list_collections(): pprint.pprint(col)

col_da = coviddb["daily.announcement"]
pprint.pprint(col_da.find_one())

## Insert document from json files
# directory = "./data/"
# for filename in os.listdir(directory):
#     print(filename)
#     with open(directory+filename) as f: file_data = json.load(f)
#     col_da.insert_one(file_data)

## Delete documents
# col_da.delete_one({"date":"2020-01-01"})

## Get death trend
death = {}
days = []
records = col_da.find({"dead":{"$exists":True}}, {"_id":0, "date":1, "dead":1}).sort("date", -1)
for x in records: 
    days.append(x["date"])
    death[x["date"]]=x["dead"]
pprint.pprint(death)
df_death = pd.DataFrame.from_dict(death, orient="index")
# df_death.index = pd.to_datetime(df_death.index)
df_death.rename(columns={0:"dead"}, inplace=True)
df_death.plot.barh()

## Find Min/Max of a date
dailyAmt = {}
for searchDate in days:
    val = []
    init_val = col_da.find_one({"date": searchDate},{"_id":0,"cases":1})
    if (init_val != None):
        val.append(int(init_val["cases"]))
    records = col_da.find({"corrections.date": searchDate}, {"_id":0, "date":1, "corrections.cases.$":1}).sort("date", 1)
    for _i, x in enumerate(records):
        val.append(int(x["corrections"][0]["cases"]))
    dailyAmt[searchDate] = {"Min":min(val), "Max":max(val)}
pprint.pprint(dailyAmt)
df_daily = pd.DataFrame.from_dict(dailyAmt, orient="index")
df_daily["7d Rolling"] = df_daily["Max"].rolling(7).mean()
pprint.pprint(df_daily)
ax = df_daily.plot(stacked=False)
plt.show()

dbclient.close()
