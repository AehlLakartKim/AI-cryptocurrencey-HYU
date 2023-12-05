#Feature: Book_I, Book_D / Midprice
#This Code is for the custom feature calculated from the ratio of Bids & Asks and traded price
import pandas as pd

def cal_ask_bid_ratio(arr):
  ask_total = 0
  bid_total = 0
  ask_count = 0
  bid_count = 0
  index = 0
  while(index < len(arr)):
    if(arr[index]["type"] == 0):
      bid_total += arr[index]["total"]
      bid_count += 1
    else:
      ask_total += arr[index]["total"]
      ask_count += 1
    index += 1
  if(bid_count == 0):
    return -1
  elif(bid_total == 0):
    return -2
  else:
    return ask_total / bid_total



dict_data = {' ': ' ', 'ask_bid_ratio':[]}
new_df = pd.DataFrame(dict_data)

FeaturePath = r"C:\Users\small\2023-11M-15_Upbit-btc-feature2.csv"
TdfPath = r"C:\Users\small\TradeBook_Upbit_2H.csv"

Featuredf = pd.read_csv(FeaturePath).apply(pd.to_numeric,errors='ignore')
Tradedf = pd.read_csv(TdfPath).apply(pd.to_numeric,errors='ignore')
TradeIndex = 0
index = 0

arr = []
same_timestamp = []
while(TradeIndex < len(Tradedf)):
  if(TradeIndex == 0 or TradeIndex == 1 or TradeIndex == 2 or TradeIndex == 3):
    arr.append(Tradedf.loc[TradeIndex])
    new_df.loc[index] = [' ', -3]
    TradeIndex += 1
    index += 1
    continue
  
  if(TradeIndex + 1 != len(Tradedf) and (Tradedf.loc[TradeIndex]["timestamp"] == Tradedf.loc[TradeIndex + 1]["timestamp"])):
    arr.append(Tradedf.loc[TradeIndex])
    arr.append(Tradedf.loc[TradeIndex + 1])
    same_timestamp.append(Tradedf.loc[TradeIndex]["timestamp"])
    ratio_data = cal_ask_bid_ratio(arr)
    TradeIndex += 2
  else:
    arr.append(Tradedf.loc[TradeIndex])
    ratio_data = cal_ask_bid_ratio(arr)
    TradeIndex += 1

  if(len(same_timestamp) >= 1 and (same_timestamp[0] == arr[0]["timestamp"])):
    arr.remove(arr[0])
    arr.remove(arr[0])
    same_timestamp.remove(same_timestamp[0])
  else:
    arr.remove(arr[0])

  new_df.loc[index] = [' ', ratio_data]

  index += 1

pd.concat([Featuredf, new_df], axis = 1).to_csv(r"C:\Users\small\2023_11_15_upbit_featureFinal.csv", index=False)