import yfinance as yf
from connection_file import client
import datetime
import time
import pytz

db_name = "options"
# all_collection_name = "allOptions"
used_collection_name = "usedOptions"
active_collection_name = "activeOptions"

db = client[db_name]
# allCollection = db[all_collection_name]
usedCollection = db[used_collection_name]
activeCollection = db[active_collection_name]

#adjuested total = 856+428 + 636+318 + 328+164 + 496+248
def current_option_price():
    #grab and format data
    i = 0
    data_list = list(activeCollection.find({}, {"data": 1, "name": 2}))
    for i in data_list:
        #check the current option price
        if i["data"]["Strategy"] == "BullPut" or i["data"]["Strategy"] == "BearCall":
            #return a list[optionPrice, stockPrice]
            optionPrice, stockPrice = regular_strategy(i["data"])
            #update this to our current active contracts
            # activeCollection.update_one({"_id": i["_id"]}, {"$set": {"data.CurrentPrice": price}})
            print("Regular Option Caluclated")
        else:
            optionPrice, stockPrice = regular_strategy(i["data"])
            print("Iron Option Caluclated")
        print(i)
        i += 1
        #update this to our current active contracts
        activeCollection.update_one({"_id": i["_id"]}, {"$set": {"data.CurrentPrice": optionPrice, "data.Price": stockPrice}})
        #update the used collection aswell

        usedCollection.update_one({"name": i["name"]}, {"$set": {"CurrentPrice": optionPrice}})
def regular_strategy(contract):
    bid = 0
    ask = 0

    if contract["Strategy"] == "BullPut" or contract["Strategy"] == "BearCall":
        symbol = contract["Symbol"]
        date = contract["Exp Date"].replace("-", "")[2:]
        optionType = ""
        if contract["Strategy"] == "BullPut":
            optionType = "P"
        elif contract["Strategy"] == "BearCall":
            optionType = "C"
        amount1 = str(contract["Leg1 Strike"] * 1000).rstrip('0').rstrip('.')
        amount2 = str(contract["Leg2 Strike"] * 1000).rstrip('0').rstrip('.')
        while len(amount1) < 8:
            amount1 = "0" + amount1
        while len(amount2) < 8:
            amount2 = "0" + amount2
        # print(amount1, amount2)
        option_list = []
        option_symbols1 = symbol + date + optionType + amount1
        option_symbols2 = symbol + date + optionType + amount2
        option_list.append([option_symbols1, "bid"])
        option_list.append([option_symbols2, "ask"])

        option_chain = yf.Ticker(symbol).option_chain(contract["Exp Date"])
        call_options = option_chain.calls
        put_options = option_chain.puts
        bid = 0
        ask = 0
        for option_symbol in option_list:
        # Get the option data for the specified option symbol
            option_data = None
            if optionType == "C":
                option_data = call_options[call_options.contractSymbol == option_symbol[0]]
            elif optionType == "P":
                option_data = put_options[put_options.contractSymbol == option_symbol[0]]

            if not option_data.empty:
                # Get the option price
                option_price = option_data.lastPrice.values[0]
                if option_symbol[1] == "ask":
                    ask = option_price
                else:
                    bid = option_price
            #     print(f"The price of the {option_symbol} call option is {option_price}")
            # else:
            #     print(f"The option symbol {option_symbol} does not exist in the option chain data.")
        currentPrice = round((bid - ask), 2)
        stockData = yf.Ticker(symbol)
        stockPrice = stockData.info["currentPrice"]
        return [currentPrice, stockPrice]
    else:
        symbol = contract["Symbol"]
        date = contract["Exp Date"].replace("-", "")[2:]
        a1 = str(float(contract["Leg1 Strike"][:-1]) * 1000).rstrip('0').rstrip('.')
        a2 = str(float(contract["Leg2 Strike"][:-1]) * 1000).rstrip('0').rstrip('.')
        a3 = str(float(contract["Leg3 Strike"][:-1]) * 1000).rstrip('0').rstrip('.')
        a4 = str(float(contract["Leg4 Strike"][:-1]) * 1000).rstrip('0').rstrip('.')
        def formatPrice(a):
            while len(a) < 8:
                a = "0" + a
            return a
        a1 = formatPrice(a1)
        a2 = formatPrice(a2)
        a3 = formatPrice(a3)
        a4 = formatPrice(a4)
        option_list = []

        o1 = symbol + date + contract["Leg1 Strike"][-1] + a1
        o2 = symbol + date + contract["Leg2 Strike"][-1] + a2
        o3 = symbol + date + contract["Leg3 Strike"][-1] + a3
        o4 = symbol + date + contract["Leg4 Strike"][-1] + a4
        option_list.append([o1, "ask", contract["Leg1 Strike"][-1]])
        option_list.append([o2, "bid", contract["Leg2 Strike"][-1]])
        option_list.append([o3, "bid", contract["Leg3 Strike"][-1]])
        option_list.append([o4, "ask", contract["Leg4 Strike"][-1]])

        option_chain = yf.Ticker(symbol).option_chain(contract["Exp Date"])
        call_options = option_chain.calls
        put_options = option_chain.puts

        ask_bid = [0,0,0,0]
        for i in range(len(option_list)):
            option_symbol = option_list[i]
            option_data = None
            if option_symbol[2] == "C":
                option_data = call_options[call_options.contractSymbol == option_symbol[0]]
            else:
                option_data = put_options[put_options.contractSymbol == option_symbol[0]]
            if not option_data.empty:
                # Get the option price
                option_price = option_data.lastPrice.values[0]
                ask_bid[i] = option_price
        total = round((ask_bid[1] - ask_bid[0]) + (ask_bid[2] - ask_bid[3]), 2)
        stockData = yf.Ticker(symbol)
        stockPrice = stockData.info["currentPrice"]
        return [total, stockPrice]
    # # Define the ticker symbol and the option symbols
    # symbol = "JPM"
    # option_symbols = ["JPM230421C00139000", "JPM230421C00140000"]

    # # Get the option chain data for the specified symbol
    # option_chain = yf.Ticker(symbol).option_chain("2023-06-16")
    # print(option_chain)
    # # Get the call options for the specified expiration date
    # call_options = option_chain.calls

    # # Loop through the option symbols and get the option prices
    # for option_symbol in option_symbols:
    #     # Get the option data for the specified option symbol
    #     option_data = call_options[call_options.contractSymbol == option_symbol]

    #     if not option_data.empty:
    #         # Get the option price
    #         option_price = option_data.lastPrice.values[0]

    #         print(f"The price of the {option_symbol} call option is {option_price}")
    #     else:
    #         print(f"The option symbol {option_symbol} does not exist in the option chain data.")
# start_time = datetime.time(9, 30, tzinfo=pytz.timezone('US/Eastern'))
# end_time = datetime.time(16, 0, tzinfo=pytz.timezone('US/Eastern'))
# while True:
#     now = datetime.datetime.now(pytz.timezone('US/Eastern'))
#     if now.weekday() < 5 and start_time <= now.time() <= end_time:
#         current_option_price()
#     time.sleep(15*60)  # Wait for 15 minutes
# current_option_price()

# symbol = "JPM"
# option_symbols = ["JPM230421C00139000", "JPM230421C00140000"]

# # Get the option chain data for the specified symbol
# option_chain = yf.Ticker(symbol).option_chain("2023-06-16")
# # Get the call options for the specified expiration date
# call_options = option_chain.calls

# # Loop through the option symbols and get the option prices
# for option_symbol in option_symbols:
#     # Get the option data for the specified option symbol
#     option_data = call_options[call_options.contractSymbol == option_symbol]

#     if not option_data.empty:
#         # Get the option price
#         option_price = option_data.lastPrice.values[0]

#         print(f"The price of the {option_symbol} call option is {option_price}")
#     else:
#         print(f"The option symbol {option_symbol} does not exist in the option chain data.")