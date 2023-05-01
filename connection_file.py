from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import TEXT
from datetime import datetime
import bson
import math

uri = "mongodb+srv://admin:yunyun520@optionx.0rjan6j.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db_name = "options"
active_collection_name = "activeOptions"
daily_collection_name = "dailyBalance"
used_collection_name = "usedOptions"

db = client[db_name]
dailyC = db[daily_collection_name]
usedC = db[used_collection_name]
activeCollection = db[active_collection_name]

# activeCollection.update_many(
#   {},
#   { "$unset": { "data._id": "" }} 
# )
# for doc in usedC.find():
#     num = math.ceil((doc["KellyCriterion"] * 2500 * 0.33) / (doc["Max Loss"] * 100))
#     usedC.update_one({"_id": doc["_id"]}, {"$set" : {"Quantity": num}})
# for doc in usedC.find():
#     num = (doc['Max Profit'] * doc['Probability']) + ((doc['Max Loss'] * -1) * (1 - doc['Probability']))
#     usedC.update_one({"_id": doc["_id"]}, {"$set": {"ExpectedValue": num}})
# for doc in activeCollection.find():
#     name = doc["data"]["Symbol"] + doc["data"]["Exp Date"] + str(doc["data"]["ExpectedValue"]) + str(doc["data"]["KellyCriterion"])
#     activeCollection.update_one(
#         {"_id": doc["_id"]},
#         {"$set": {"name": name}}
#     )
# for doc in usedC.find():
#     name = doc['Symbol'] + doc["Exp Date"] + str(doc["ExpectedValue"]) + str(doc["KellyCriterion"])
#     usedC.update_one(
#         {"_id": doc["_id"]},
#         {"$set": {"name": name}}
#     )

# for doc in activeCollection.find():
#     quantity = math.ceil(doc["data"]["KellyCriterion"] * 2500 / (doc["data"]["Max Loss"] * 100))
#     activeCollection.update_one(
#         {"_id": doc["_id"]},
#         {"$set": {"data.Quantity": quantity}}
#     )
# for doc in usedC.find():
#     quantity = math.ceil(doc["KellyCriterion"] * 2500 / (doc["Max Loss"] * 100))
#     usedC.update_one(
#         {"_id": doc["_id"]},
#         {"$set": {"Quantity": quantity}}
#     )
# activeCollection.update_many({}, {"$unset": {"Quantity": ""}})
# utc_now = datetime.utcnow()
# utc_now_str = utc_now.strftime('%Y-%m-%d')
# # utc_bson = bson.UTCDateTime(int(utc_now.timestamp() * 1000))
# balance = 8992
# dailyC.insert_one({"date": utc_now_str, 
#                    "hour": {
#         f"{utc_now.hour}-{utc_now.minute}": balance
#                    },
#                    "balance": balance})

# newField = {"CurrentPrice": 0}
# removeField = "CurrentPrice"
# usedC.update_many({}, {"$set": newField})
# activeCollection.create_index("expiration", expireAfterSeconds=5)

# activeCollection.create_index([
#     ("data.Symbol", 1),
#     ("data.Exp Date", 1),
#     ("data.Leg1 Strike", 1),
#     ("data.Leg2 Strike", 1)
# ], unique=True)

# allC.create_index([("Symbol", 1), ("Exp Date", 1), ("Leg1 Strike", 1), ("Leg2 Strike", 1)], unique=True)
# usedC.create_index([("Symbol", 1), ("Exp Date", 1), ("Leg1 Strike", 1), ("Leg2 Strike", 1)], unique=True)