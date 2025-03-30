import finnhub
import alpaca_trade_api as alpaca
import random
import requests

# set up market api client
market_key = "cvkbmnpr01qu5brnqs70cvkbmnpr01qu5brnqs7g"
finnhub_client = finnhub.Client(api_key = market_key)

# set up Alpaca API client (paper trading API keys)
alpaca_key = "PKBN3BLX4PQHOCZ00QPZ"
secret_key = "9fA1vekjReQggjB36H7lIUtDwVo7T2XbwdelGUIE"
alpaca_api = alpaca.REST(alpaca_key, secret_key, "https://paper-api.alpaca.markets", api_version='v2')
account = alpaca_api.get_account()

# SPY: S&P ETF, DIA: Dow ETF, QQQ: Nasdaq ETF
etf_index = "SPY", "DIA", "QQQ"
dps = []

# determine percent change (dp) for each ETF
for index in etf_index:
    current_index = finnhub_client.quote(index)
    print(current_index)
    dps.append(current_index["dp"])

# determine average dp for overall market trend
average_dp = 3
print(average_dp)

# assign investment amount and buy/sell based off market trend
if average_dp>0.5:
    mcdonald_meal = 3.17, "buy"
elif average_dp <-0.5:
    mcdonald_meal = 2.61, "sell"
else:
    mcdonald_meal = 2.95, random.choice(["buy", "sell"])

headers = {
    "APCA-API-KEY-ID": alpaca_key,
    "APCA-API-SECRET-KEY": secret_key,
    "accept": "application/json",
    "content-type": "application/json"
}

payload = {
        "type": "market",
        "time_in_force": "day",
        "side": mcdonald_meal[1]
}

if mcdonald_meal[1] == "buy":
    # collect stock symbols
    stocks = finnhub_client.stock_symbols("US")
    filtered_stock = False

    # filter stocks based on market cap to above 100 billion
    if stocks:
        while not filtered_stock:
            stock_symbol = random.choice(stocks)["displaySymbol"]
            try:
                profile = finnhub_client.company_profile2(symbol=stock_symbol)
                market_cap = profile.get("marketCapitalization")
                asset = alpaca_api.get_asset(stock_symbol)
            except Exception as e:
                print(f"Error retrieving data for {stock_symbol}: {e}")
                continue
            
            # Check if market cap meets threshold and asset is active/tradable
            if market_cap is not None and market_cap > 100000:
                if asset.status == "active" and asset.tradable:
                    filtered_stock = True            

    # place order
    print("Buying $", mcdonald_meal[0], "of", stock_symbol)
    response = requests.post("https://paper-api.alpaca.markets/v2/orders", json=payload, headers=headers)

else:
    # ensure there is a position to sell and the value is greater than the meal amount
    response = requests.get("https://paper-api.alpaca.markets/v2/positions", headers=headers)
    positions = response.json()  # Parse the JSON response

    # check there are positions
    if len(positions) == 0:
        print("No positions found. Cannot sell or execute order.")
    else:
        print("Positions:", positions)
        # choose random position and determine nominal value
        random_position = random.choice(positions) 
        quantity = random_position["qty"]
        market_value = random_position["market_value"]
        nominal_value = quantity*market_value

        # set payload symbol
        payload["symbol"] = random_position["symbol"]

        # either set payload value as meal amount or nominal value owned
        if (mcdonald_meal[0]>nominal_value):
            payload["notional"] = nominal_value 
        else:
            payload["notional"] = mcdonald_meal[0]
        
        # place order
        print("Selling", payload["notational"], "of", random_position["symbol"])
        response = requests.post("https://paper-api.alpaca.markets/v2/orders", json=payload, headers=headers)


