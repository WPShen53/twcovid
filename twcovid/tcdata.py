from typing import Collection
import pymongo
import os
import json
import pandas as pd

def get_docs():
    db_client = pymongo.MongoClient("mongodb://localhost:27017")
    covid_db = db_client["tw_covid"]
    documents = covid_db["daily.announcement"]
    return documents

def refresh_data_from_json():
    docs = get_docs()
    delete_all_docs(docs)
    insert_json_from_dir(docs = docs) 

def delete_all_docs(docs = get_docs()):
    docs.delete_many({})

def insert_json_from_dir(dir = './data/', docs = get_docs()):
    try: 
        for filename in os.listdir(dir):
            with open(dir+filename) as f: file_data = json.load(f)
            if isinstance(file_data, dict): 
                docs.insert_one(file_data)
            else : 
                docs.insert_many(file_data)
    except:
        pass

def get_death_df(docs = get_docs()):
    death = {}
    records = docs.find({"dead":{"$exists":True}}, {"_id":0, "date":1, "dead":1}).sort("date", 1)
    for x in records: 
        death[x["date"]]=int(x["dead"])
    df_death = pd.DataFrame.from_dict(death, orient="index")
    df_death.index = pd.to_datetime(df_death.index)
    df_death.rename(columns={0:"dead"}, inplace=True)
    return df_death

def get_twcovid_df_from_db():
    docs = get_docs()
    daily_amt = {}
    for x in docs.find({}):
        val = []
        searchDate = x["date"]
        init_val = docs.find_one({"date": searchDate},{"_id":0,"cases":1})
        if (init_val != None):
            val.append(int(init_val["cases"]))
        records = docs.find({"corrections.date": searchDate}, {"_id":0, "date":1, "corrections.cases.$":1}).sort("date", 1)
        for _i, x in enumerate(records):
            val.append(int(x["corrections"][0]["cases"]))
        daily_amt[searchDate] = {"Original":min(val), "Corrected":max(val), "Updates":len(val)}
    df_daily = pd.DataFrame.from_dict(daily_amt, orient="index")
    df_daily.index = pd.to_datetime(df_daily.index)
    df_daily.index.rename('date', inplace=True)
    df_daily["7d Rolling"] = df_daily["Corrected"].rolling(7, center=True).mean()
    df_daily["dead"] = get_death_df(docs)
    return df_daily