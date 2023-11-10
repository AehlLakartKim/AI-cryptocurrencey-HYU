import requests
import pandas as pd
import json
import time


from datetime import datetime
def TimeConverter(TimeValue):

    timestamp_int = int(TimeValue) / 1000  # 밀리초(ms)를 초(s)로 변환

    # timestamp를 년, 월, 일, 시, 분, 초로 변환
    dt_object = datetime.utcfromtimestamp(timestamp_int)

    ormatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    
    return ormatted_time



CurrentIndex = 0
BidAskIndex = 0

url = "https://api.bithumb.com/public/orderbook/BTC_KRW/?count=1"

headers = {"accept": "application/json"}


dict_data = {'price':[], 'quantity':[], 'type':[], 'timestamp':[]}


response = requests.get(url, headers=headers).json()

#df.loc[0] = [0, 0, 0]

while(1):
    response = requests.get(url, headers=headers).json()
    
    
    if(CurrentIndex == 0):
        df = pd.DataFrame(dict_data)
        CurrentIndex = 1
    else:
        if(BidAskIndex == 0):
            df.loc[CurrentIndex] = [float(response['data']['bids'][0]['price']), float(response['data']['bids'][0]["quantity"]), BidAskIndex, TimeConverter(response['data']["timestamp"])]
            if(CurrentIndex % 10 == 0):
                if(BidAskIndex == 0):
                    BidAskIndex = 1
                else:
                    BidAskIndex = 0     
        elif(BidAskIndex == 1):
            df.loc[CurrentIndex] = [float(response['data']['asks'][0]['price']), float(response['data']['asks'][0]["quantity"]), BidAskIndex, TimeConverter(float(response['data']["timestamp"]))]
            if(CurrentIndex % 10 == 0):
                if(BidAskIndex == 0):
                    BidAskIndex = 1
                else:
                    BidAskIndex = 0
                
        CurrentIndex += 1
        
    if(CurrentIndex % 50 == 0):
        df.to_csv(r"C:\Users\small\Test.csv ", index=False)





