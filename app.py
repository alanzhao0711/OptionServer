from flask import Flask
from flask_socketio import SocketIO, emit
import pandas as pd
import os
from flask_cors import CORS
from connection_file import client
import datetime
import bson
import sched
import time
import math
import pytz
from DownloadCSV import download
from Compute import generateNewestIronConorsEV
from OptionPrice import current_option_price

app = Flask(__name__)
CORS(app,resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

db_name = "options"
daily_collection_name = "dailyBalance"
used_collection_name = "usedOptions"
active_collection_name = "activeOptions"

db = client[db_name]
dailyC = db[daily_collection_name]
usedCollection = db[used_collection_name]
activeCollection = db[active_collection_name]
@app.route("/getMarketData")
def get_market_data():
    try:
    #download the data from the website
        download("BearCall", "https://www.barchart.com/options/call-spreads/bear-call?orderBy=maxProfitPercent&orderDir=desc")
        download("BullPut", "https://www.barchart.com/options/put-spreads/bull-put?orderBy=maxProfitPercent&orderDir=desc")
        download("IronCon", "https://www.barchart.com/options/short-condors?orderBy=breakEvenProbability&orderDir=desc")
        
        #analyze data 
        generateNewestIronConorsEV("BearCall")
        generateNewestIronConorsEV("BullPut")
        generateNewestIronConorsEV("IronCon")
        return "Successfully"
    except:
        return "Failed, check errors"

@app.route("/getCurrentMarketPrice")
def get_current_market_price():
    try:
        current_option_price()
        return "Option price updated!"
    except:
        return "Errors, check server log"
    
@app.route('/data/<string:folder_name>')
def get_data(folder_name):
    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), folder_name)

    # Get the list of CSV files in the files directory
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

    # Find the most recent CSV file based on the file creation time
    newest_file = max(csv_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))

    # Load the CSV file into a DataFrame
    df = pd.read_csv(os.path.join(data_dir, newest_file))
    
    # Select the top 10 rows from the DataFrame
    df_top_10 = df.head(10)
    df_top_10["Purchased"] = (df_top_10["ExpectedValue"] > 0) & (df_top_10["KellyCriterion"] > 0)
    df_top_10["Strategy"] = folder_name
    df_top_10["CurrentPrice"] = df_top_10["Max Profit"]
    df_top_10["Quantity"] = df_top_10.apply(lambda row: math.ceil((row["KellyCriterion"] * 2500)*0.33 / (row["Max Loss"]*100)) if row["Purchased"] else 0, axis=1)
    data = df_top_10.to_dict('records')

    #add all of the data to my all contract collection
    # allCollection.insert_many(data)

    for doc in data:
        if doc["Purchased"]:
            #add doc to my usedCollection used for history of contract purchased
            name = doc["Symbol"] + doc["Exp Date"] + str(doc["ExpectedValue"]) + str(doc["KellyCriterion"])
            try:
                usedCollection.insert_one({doc, {"name": name}})
            except:
                print("Contract already purchased")
            exp_date = datetime.datetime.strptime(doc["Exp Date"], "%Y-%m-%d").replace(hour=20, minute=30, second=0)
            bson_date = bson.datetime.datetime(exp_date.year, exp_date.month, exp_date.day,
                                        exp_date.hour, exp_date.minute, exp_date.second)
            
            # now = datetime.datetime.utcnow()
            # b_now = bson.datetime.datetime(now.year, now.month, now.day,
            #                             now.hour, now.minute, now.second)
            try:
                activeCollection.insert_one({"data": doc, "expiration": bson_date, "name": name})
            except:
                print("Contract already purchased")
    json_data = df_top_10.to_json(orient='records')
    return json_data


@socketio.on("dash")
def connected():
    """event listener when client connects to the server"""
    #SEND BASIC INFO (NUM) TO DASHBAORD
    num_transactions = db[used_collection_name].count_documents({})
    num_active = db[active_collection_name].count_documents({})
    emit("dashboard-nums", {"num_transactions": num_transactions, "active": num_active})

    #SEND DASHBOARD CARD INFORMATION TO CLIENT
    dashboardData = list(activeCollection.find({}, {"_id": 0, "data": 1}).sort([('$natural', -1)]))
    formatedDashboard = []
    for i in dashboardData:
        for k, v in i.items():
            formatedDashboard.append((v))
    for item in formatedDashboard:
        item['_id'] = str(item['_id'])
    emit("active-dash", formatedDashboard[:6])
    emit("all-active-options", formatedDashboard)
    #UPDATE CURRENT BALANCE
    # calculate the current balance by computing the price of all active
    # contracts, our inital balance is 10,000

    total = 0
    for i in usedCollection.find():
        total += ((i["Max Profit"] - i["CurrentPrice"]) * 100) * i["Quantity"]
    newTotal = 10000 + total
    emit("current-balance", newTotal)
    emit("account-PL", total)
    # UPDATE DAILY BALANCE
    #update or create the current balance to showcase in chart
    utc_now = datetime.datetime.utcnow()
    utc_now_str = utc_now.strftime('%Y-%m-%d')
    utc_tz = pytz.timezone('UTC')
    ny_tz = pytz.timezone('America/New_York')
    ny_now = utc_tz.localize(utc_now).astimezone(ny_tz)
    ny_date_str = ny_now.strftime('%Y-%m-%d')

    # Construct a query that matches documents with the current date
    query = {'date': ny_date_str}
    update = {
        "$set": {
            "balance": newTotal,
            f"hour.{ny_now.hour}-{ny_now.minute}": newTotal
        },
    }
    dailyC.update_one(query, update, upsert=True)

    #grab daily chart data
    dailyChart = dailyC.find_one(query, {"_id": 0, "hour": 1})
    hour_list = []
    for key, value in dailyChart['hour'].items():
        hour_list.append({'hour': key, 'balance': value})
    emit("daily-info", hour_list)

@socketio.on("account")
def account_related_info():
    #grab account chart data
    dailyChart = list(dailyC.find({}, {"_id":0, "date":1, "balance":2}))
    emit("account-chart", dailyChart)

    #find amount earned today
    amountEarned = list(dailyC.find({}, {"_id":0, "balance": 1}).sort([('$natural', -1)]).limit(2))
    earnedToday = amountEarned[0]["balance"] - amountEarned[1]["balance"]
    percent = ((amountEarned[0]["balance"] - amountEarned[1]["balance"]) / amountEarned[0]["balance"])*100
    emit("earned-today", [earnedToday, round(percent, 2)])


@socketio.on("transactions")
def return_all_past_transactions():
    #return past transactions
    past = list(usedCollection.find({}))
    for item in past:
        item['_id'] = str(item['_id'])
    emit("past", past)


@app.route("/")
def index():
    return "Hello world"

@socketio.on('connect')
def handle_connect():
    socketio.emit('message', 'Hello world!')

if __name__ == "__main__":
    # app.run(debug=True, port=os.environ.get('PORT', 5000))
    socketio.run(app)
