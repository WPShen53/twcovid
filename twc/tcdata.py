import pymongo
import pkg_resources
import json
import os
import pandas as pd

def __get_docs(db_str):
    db_client = pymongo.MongoClient(db_str)
    covid_db = db_client["tw_covid"]
    documents = covid_db["daily.announcement"]
    return documents

def refresh_data_from_json(dir = '../data/', db_str=''):
    if db_str=='':
        print('Did not provide MongoDB connection str. Use defaul "mongodb://localhost:27017"')
        db_str = 'mongodb://localhost:27017'
    try: 
        docs = __get_docs(db_str)
        docs.delete_many({})
        for filename in os.listdir(dir):
            with open(dir+filename) as f: file_data = json.load(f)
            if isinstance(file_data, dict): 
                docs.insert_one(file_data)
            else : 
                docs.insert_many(file_data)
    except Exception as err:
        print("fail to insert data from json file. {}".format(err))

def get_twcovid_df (from_db = True, db_str="mongodb://localhost:27017"):
    if from_db == False:
        df = load_twcovid()
    else:
        try:
            df = get_twcovid_df_from_db(db_str)
        except Exception as err:
            print ('Unable to connect to db {}'.format(err))
            print ('=== Get dataframe from csv ===')
            df = load_twcovid()
    return df

def get_twcovid_df_from_db(db_str):
    docs = __get_docs(db_str)
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
        daily_amt[searchDate] = {"Original":min(val), "Corrected":max(val)}
    df = pd.DataFrame.from_dict(daily_amt, orient="index")
    df.index = pd.to_datetime(df.index)
    df.index.rename('date', inplace=True)
    df["7d Rolling"] = df["Corrected"].rolling(7, center=True).mean()
 
    death = {}
    records = docs.find({"dead":{"$exists":True}}, {"_id":0, "date":1, "dead":1}).sort("date", 1)
    for x in records: 
        death[x["date"]]=int(x["dead"])
    df_death = pd.DataFrame.from_dict(death, orient="index")
    df_death.index = pd.to_datetime(df_death.index)
    df_death.rename(columns={0:"dead"}, inplace=True)
    df["dead"] = df_death
    return df

def load_twcovid():
    stream = pkg_resources.resource_stream(__name__, 'dailyDF.csv')
    df = pd.read_csv(stream)
    df.drop(columns=['Updates'], inplace=True)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df
