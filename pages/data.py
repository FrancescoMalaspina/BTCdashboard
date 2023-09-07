import pandas as pd

BTCprice = pd.read_csv("database/BTC-USD.csv")
BTCprice["Date"] = pd.to_datetime(BTCprice["Date"], format="%Y-%m-%d")