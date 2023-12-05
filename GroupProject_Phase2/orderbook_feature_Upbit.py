#Feature: Book_I, Book_D / Midprice

import pandas as pd
import time #For Debugging
import math

interval = 1
ratio = 0.2

def cal_mid_price(gr_bid_level, gr_ask_level):
  if len(gr_bid_level) > 0 and len(gr_ask_level) > 0:
    bid_top_price = gr_bid_level.iloc[0].price
    bid_top_level_qty = gr_bid_level.iloc[0].quantity
    ask_top_price = gr_ask_level.iloc[0].price
    ask_top_level_qty = gr_ask_level.iloc[0].quantity
    
    mid_price_wt = (gr_bid_level.iloc[2].price + gr_ask_level.iloc[2].price) * 0.5
    mid_price = (gr_bid_level.iloc[0].price + gr_ask_level.iloc[0].price) * 0.5
    mid_price_mkt = ((bid_top_price * ask_top_level_qty) + (ask_top_price * bid_top_level_qty)) / (bid_top_level_qty+ask_top_level_qty)
    mid_price_vmap = ((gr_bid_level['price'] * gr_bid_level['quantity']).sum() + (gr_ask_level['price'] * gr_ask_level['quantity']).sum()) / (gr_bid_level['quantity'].sum() + gr_ask_level['quantity'].sum())

    return mid_price, mid_price_mkt, mid_price_vmap, mid_price_wt

# book imbalance

# @params

# gr_bid_level: all bid level
# gr_ask_level: all ask level
# diff: summary of trade, refer to get_diff_count_units()
# var: can be empty
# mid: midprice


def live_cal_book_i_v1(param, gr_bid_level, gr_ask_level, var, mid):
    
    mid_price = mid

    ratio = param[0]; level = param[1]; interval = param[2]
    #print ('processing... %s %s,level:%s,interval:%s' % (sys._getframe().f_code.co_name,ratio,level,interval)), 
    
        
    #_flag = var['_flag']
        
    #if _flag: #skipping first line
    #    var['_flag'] = False
    #    return 0.0

    quant_v_bid = gr_bid_level.quantity**ratio
    price_v_bid = gr_bid_level.price * quant_v_bid

    quant_v_ask = gr_ask_level.quantity**ratio
    price_v_ask = gr_ask_level.price * quant_v_ask
 
    #quant_v_bid = gr_r[(gr_r['type']==0)].quantity**ratio
    #price_v_bid = gr_r[(gr_r['type']==0)].price * quant_v_bid

    #quant_v_ask = gr_r[(gr_r['type']==1)].quantity**ratio
    #price_v_ask = gr_r[(gr_r['type']==1)].price * quant_v_ask
        
    askQty = quant_v_ask.values.sum()
    bidPx = price_v_bid.values.sum()
    bidQty = quant_v_bid.values.sum()
    askPx = price_v_ask.values.sum()
    bid_ask_spread = interval
        
    book_price = 0 #because of warning, divisible by 0
    if bidQty > 0 and askQty > 0:
        book_price = (((askQty*bidPx)/bidQty) + ((bidQty*askPx)/askQty)) / (bidQty+askQty)

        
    indicator_value = (book_price - mid_price) / bid_ask_spread
    #indicator_value = (book_price - mid_price)
    
    return indicator_value



def live_cal_book_d_v1(param, gr_bid_level, gr_ask_level, diff, var, mid):

    #print gr_bid_level
    #print gr_ask_level

    ratio = param[0]; level = param[1]; interval = param[2]
    #print ('processing... %s %s,level:%s,interval:%s' % (sys._getframe().f_code.co_name,ratio,level,interval)), 

    decay = math.exp(-1.0/interval)
    
    _flag = var['_flag']
    prevBidQty = var['prevBidQty']
    prevAskQty = var['prevAskQty']
    prevBidTop = var['prevBidTop']
    prevAskTop = var['prevAskTop']
    bidSideAdd = var['bidSideAdd']
    bidSideDelete = var['bidSideDelete']
    askSideAdd = var['askSideAdd']
    askSideDelete = var['askSideDelete']
    bidSideTrade = var['bidSideTrade']
    askSideTrade = var['askSideTrade']
    bidSideFlip = var['bidSideFlip']
    askSideFlip = var['askSideFlip']
    bidSideCount = var['bidSideCount']
    askSideCount = var['askSideCount'] 
  
    curBidQty = gr_bid_level['quantity'].sum()
    curAskQty = gr_ask_level['quantity'].sum()
    curBidTop = gr_bid_level.iloc[0].price #what is current bid top?
    curAskTop = gr_ask_level.iloc[0].price

    #curBidQty = gr_r[(gr_r['type']==0)].quantity.sum()
    #curAskQty = gr_r[(gr_r['type']==1)].quantity.sum()
    #curBidTop = gr_r.iloc[0].price #what is current bid top?
    #curAskTop = gr_r.iloc[level].price

    if _flag:
        var['prevBidQty'] = curBidQty
        var['prevAskQty'] = curAskQty
        var['prevBidTop'] = curBidTop
        var['prevAskTop'] = curAskTop
        var['_flag'] = False
        return 0.0
    
     
    if curBidQty > prevBidQty:
        bidSideAdd += 1
        bidSideCount += 1
    if curBidQty < prevBidQty:
        bidSideDelete += 1
        bidSideCount += 1
    if curAskQty > prevAskQty:
        askSideAdd += 1
        askSideCount += 1
    if curAskQty < prevAskQty:
        askSideDelete += 1
        askSideCount += 1
        
    if curBidTop < prevBidTop:
        bidSideFlip += 1
        bidSideCount += 1
    if curAskTop > prevAskTop:
        askSideFlip += 1
        askSideCount += 1

    
    diffDict = {"_count_1":diff[0],"_count_0":diff[1],"_units_traded_1":diff[2],"_units_traded_0":diff[3],"_price_1":diff[4],"_price_0":diff[5]}
    print(diffDict)
    #_count_1 = (diff[(diff['type']==1)])['count'].reset_index(drop=True).get(0,0)
    #_count_0 = (diff[(diff['type']==0)])['count'].reset_index(drop=True).get(0,0)
    
    bidSideTrade += diffDict["_count_1"]
    bidSideCount += diffDict["_count_1"]
    
    askSideTrade += diffDict["_count_0"]
    askSideCount += diffDict["_count_0"]
    

    if bidSideCount == 0:
        bidSideCount = 1
    if askSideCount == 0:
        askSideCount = 1

    bidBookV = (-bidSideDelete + bidSideAdd - bidSideFlip) / (bidSideCount**ratio)
    askBookV = (askSideDelete - askSideAdd + askSideFlip ) / (askSideCount**ratio)
    tradeV = (askSideTrade/askSideCount**ratio) - (bidSideTrade / bidSideCount**ratio)
    bookDIndicator = askBookV + bidBookV + tradeV
        
       
    var['bidSideCount'] = bidSideCount * decay #exponential decay
    var['askSideCount'] = askSideCount * decay
    var['bidSideAdd'] = bidSideAdd * decay
    var['bidSideDelete'] = bidSideDelete * decay
    var['askSideAdd'] = askSideAdd * decay
    var['askSideDelete'] = askSideDelete * decay
    var['bidSideTrade'] = bidSideTrade * decay
    var['askSideTrade'] = askSideTrade * decay
    var['bidSideFlip'] = bidSideFlip * decay
    var['askSideFlip'] = askSideFlip * decay

    var['prevBidQty'] = curBidQty
    var['prevAskQty'] = curAskQty
    var['prevBidTop'] = curBidTop
    var['prevAskTop'] = curAskTop
    #var['df1'] = df1
 
    return bookDIndicator


def get_diff_count_units (diff):
    
    _count_1 = _count_0 = _units_traded_1 = _units_traded_0 = 0
    _price_1 = _price_0 = 0

    diff_len = len (diff)
    if diff_len == 1:
        row = diff.iloc[0]
        if row['type'] == 1:
            _count_1 = row['count']
            _units_traded_1 = row['units_traded']
            _price_1 = row['price']
        else:
            _count_0 = row['count']
            _units_traded_0 = row['units_traded']
            _price_0 = row['price']

        return (_count_1, _count_0, _units_traded_1, _units_traded_0, _price_1, _price_0)

    elif diff_len == 2:
        row_1 = diff.iloc[1]
        row_0 = diff.iloc[0]
        _count_1 = row_1['count']
        _count_0 = row_0['count']

        _units_traded_1 = row_1['units_traded']
        _units_traded_0 = row_0['units_traded']
        
        _price_1 = row_1['price']
        _price_0 = row_0['price']

        return (_count_1, _count_0, _units_traded_1, _units_traded_0, _price_1, _price_0)

#Frametdf = AnyFrame (gr_bid_level, gr_ask_level)
def Get_diffSet (Framedf, Frametdf, TradeIndex, TdfPath):
  CurrentTimestamp = 0.0
  print(TradeIndex)
  while(True):
    if(Frametdf.timestamp[TradeIndex] == Framedf.iloc[0]["timestamp"]):
      CurrentTimestamp = Frametdf.timestamp[TradeIndex]
      print(CurrentTimestamp)
      break
    else:
      TradeIndex += 1
  
  if(Frametdf.timestamp[TradeIndex+1] == CurrentTimestamp):
    try:
      diffSetReseult = pd.read_csv(TdfPath, header=0, skiprows=range(1, TradeIndex+1), nrows=2)
      TradeIndex += 2
    except:
      print("Done")
  elif(Frametdf.timestamp[TradeIndex+1] != CurrentTimestamp):
    try:
      diffSetReseult = pd.read_csv(TdfPath, header=0, skiprows=range(1, TradeIndex+1), nrows=1)
      TradeIndex += 1
    except:
      print("Done")
    

  print(diffSetReseult)
  return diffSetReseult, TradeIndex
  

var = {'_flag':True,'prevBidQty':0,'prevAskQty':0,'prevBidTop':0,'prevAskTop':0,'bidSideAdd':0,'bidSideDelete':0,'askSideAdd':0,'askSideDelete':0,'bidSideTrade':0,'askSideTrade':0,'bidSideFlip':0,'askSideFlip':0,'bidSideCount':0,'askSideCount':0}

delta = 0.0
imbalance = 0.0

paramset = [0.2,15,1]
dict_data = {'mid_price':[], 'mid_price_mkt':[], 'mid_price_vmap':[], 'mid_price_wt':[], 'imbalance':[], 'delta': [], 'timestamp':[]}
new_df = pd.DataFrame(dict_data)

dfPath = r"C:\Users\small\OrderBook_Upbit_2H.csv"
TdfPath = r"C:\Users\small\TradeBook_Upbit_2H.csv"


df= pd.read_csv(dfPath).apply(pd.to_numeric,errors='ignore')

Tradedf = pd.read_csv(TdfPath).apply(pd.to_numeric,errors='ignore')
TradeIndex = 0

index = 0

while(index < len(df) / 30):

  bid_start = 0 + 30 * index
  bid_end = 14 + 30 * index
  ask_start = 15 + 30 * index
  ask_end = 29 + 30 * index

  gr_bid_level= df[bid_start: bid_end]
  gr_ask_level= df[ask_start: ask_end]

  #prev_gr_bid_level= df[bid_start-10: bid_end-10]
  #prev_gr_ask_level= df[ask_start-10: ask_end-10]

  mid_price, mid_price_mkt, mid_price_vmap, mid_price_wt = cal_mid_price(gr_bid_level, gr_ask_level)

  if(index != 0):
    imbalance = live_cal_book_i_v1(paramset, gr_bid_level, gr_ask_level, [], mid_price)
  
  Tempdiff, TradeIndex = Get_diffSet(gr_bid_level,Tradedf,TradeIndex,TdfPath)
  diff_set = get_diff_count_units (Tempdiff)
  delta = live_cal_book_d_v1(paramset, gr_bid_level, gr_ask_level, diff_set, var, mid_price)

  new_df.loc[index] = [mid_price, mid_price_mkt, mid_price_vmap, mid_price_wt, imbalance, delta, df.iloc[bid_start+1]["timestamp"]]
  index += 1
  
  if(index % 100 == 0):
    new_df.to_csv(r"C:\Users\small\2023-11M-15_Upbit-btc-feature2.csv ", index=False)
new_df.to_csv(r"C:\Users\small\2023-11M-15_Upbit-btc-feature2.csv ", index=False)

