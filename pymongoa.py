import pymongo
import json

dbclient = pymongo.MongoClient('mongodb://localhost:27017')
coviddb = dbclient['tw_covid']
col_da = coviddb['daily.announcement']

with open('./data/tw20210605.json') as f:
    file_data = json.load(f)

col_da.insert_one(file_data)
print(dbclient.list_database_names())

dbclient.close()
