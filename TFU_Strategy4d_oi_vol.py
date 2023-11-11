#DISCLAIMER:
#1) This sample code is for learning purposes only.
#2) Always be very careful when dealing with codes in which you can place orders in your account.
#3) The actual results may or may not be similar to backtested results. The historical results do not guarantee any profits or losses in the future.
#4) You are responsible for any losses/profits that occur in your account in case you plan to take trades in your account.
#5) TFU and Aseem Singhal do not take any responsibility of you running these codes on your account and the corresponding profits and losses that might occur.


import threading
import time

from kiteconnect import KiteConnect
from datetime import datetime,timedelta
from pytz import timezone
import ta    #Python TA Lib
import pandas as pd
import pandas_ta as pta    #Pandas TA Libv
import requests
import os

#This function helps to create OHLC candles. You have to pass the stock name + timeframe
def ohlc(checkInstrument,timeframe):
    date=pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
    while(str(date)[-2::]!='00'):
        date=pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))
    date=date+timedelta(minutes=timeframe)
    current=date
    date=date-timedelta(seconds=2)
    l=[]
    volume=0
    oi=0
    while(pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S'))<=date):
        x=getLTP(checkInstrument)
        time.sleep(1)
        if x!=[]:
            l.append(x[0])
            volume+=x[1]
            oi=x[2]
    if l!=[]:
        opens=l[0]
        high=max(l)
        low=min(l)
        close=l[-1]
        return [current,opens,high,low,close,volume,oi]
    else:
        return [-1]

def getLTP(name):
    ltp=[]
    try:
        ltp.append(kc.quote([name])[name]['last_price'])
        ltp.append(kc.quote([name])[name]['volume'])
        ltp.append(kc.quote([name])[name]['oi'])
        return ltp

    except Exception as e:
        print(name , "Failed : {} ".format(e))



def findStrikePriceATM(stock, cepe):
    global tradeCEoption
    global tradePEoption
    print(" Finding ATM ")
    global kc
    global clients
    global SL_percentage

    if (stock == "banknifty"):
        name = "NSE:"+"NIFTY BANK"   #"NSE:NIFTY BANK"
    elif (stock == "nifty"):
        name = "NSE:"+"NIFTY 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #22OCT

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)

    if (stock == "banknifty"):
        for i in range(-8, 8):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
        print(strikeList)
        for strike in strikeList:
            diff = abs(ltp - strike)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike = strike
                prev_diff = diff


    elif (stock == "nifty"):
        for i in range(-5, 5):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
            strikeList.append(strike+50)
        print(strikeList)
        for strike in strikeList:
            diff=abs(ltp - strike)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike=strike
                prev_diff=diff

    print("closest",closest_Strike)
    closest_Strike_CE = closest_Strike+otm
    closest_Strike_PE = closest_Strike-otm

    if (stock == "banknifty"):
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif (stock == "nifty"):
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if (cepe == "CE"):
        #BUY AT MARKET PRICE
        print("In CE placeorder")
        for client in clients:
            print("\n============_Placing_Trades_=====================")
            print("userID = ", client['userID'])
            broker = client['broker']
            uid = client['userID']
            key = client['apiKey']
            token = client['accessToken']
            qty = client['qty']
            oidentry = placeOrderSingle( atmCE, "BUY", qty, "MARKET", 0, "regular")
            tradeCEoption = atmCE
    else:
        #BUY AT MARKET PRICE
        print("In PE placeorder")
        for client in clients:
            print("\n============_Placing_Trades_=====================")
            print("userID = ", client['userID'])
            broker = client['broker']
            uid = client['userID']
            key = client['apiKey']
            token = client['accessToken']
            qty = client['qty']
            oidentry = placeOrderSingle( atmPE, "BUY", qty, "MARKET", 0, "regular")
            tradePEoption = atmPE

    return oidentry



def exitPosition(tradeOption):
    #Sell existing option
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']
        oidentry = placeOrderSingle( tradeOption, "SELL", qty, "MARKET", 0, "regular")
        return oidentry

def placeOrderSingle(inst ,t_type,qty,order_type,price,variety):
    exch = inst[:3]
    symb = inst[4:]
    papertrading = 0 #if this is 1, then real trades will be placed
    dt = datetime.now()
    print(dt.hour,":",dt.minute,":",dt.second ," => ",t_type," ",symb," ",qty," ",order_type," @ price =  ",price)
    try:
        if (papertrading == 1):
            order_id  = kc.place_order( variety = variety,
                                        tradingsymbol= symb ,
                                        exchange= exch,
                                        transaction_type= t_type,
                                        quantity= qty,
                                        order_type=order_type,
                                        product=kc.PRODUCT_MIS,
                                        price=price,
                                        trigger_price=price)


            print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , int(order_id) )
            return order_id
        else:
            return 0

    except Exception as e:
        print(dt.hour,":",dt.minute,":",dt.second ," => ", symb , "Failed : {} ".format(e))

####################__INPUT__#####################

api_key = "y7ypl6k1fboc5tb4"
access_token = "2ZP34JlZ46LncYRKnd2LM6X2yQsmtFys"
kc = KiteConnect(api_key=api_key)
kc.set_access_token(access_token)

checkInstrument = "NFO:NIFTY22DECFUT";
tradeCEoption = ""
tradePEoption = ""

clients = [
    {
        "broker": "zerodha",
        "userID": "",
        "apiKey": "",
        "accessToken": "",
        "qty" : 50
    }
]

expiry = {
    "year": "22",
    "month": "N",
    "day": "10",
}
otm = 0

x = 1
close=[]   #close[17873, 17777, 17772]
opens=[]
high=[]
low=[]
volume=[]
oi=[]


#-----------If there is any previous data, we will copy it------------
p = os.path.join(os.getcwd(), 'lists.csv')
if os.path.isfile(p):
    df_read = pd.read_csv('lists.csv')
    for i in range(0,len(df_read)):
        close.insert(len(close),df_read['close'][i])
        opens.insert(len(opens),df_read['opens'][i])
        high.insert(len(high),df_read['high'][i])
        low.insert(len(low),df_read['low'][i])


op=['supertrend',10,3]
print(['datetime','open','high','low','close'])
gt=1
lt=1
xx = 2
firsttrade = 0
maxtrade = 0
while x == 1:
    data=ohlc(checkInstrument,1)  #[9:20, 17000, 17870, 16780, 17220, 17556] timeframe
    dt1 = datetime.now()
    if data[0]!=-1:
        opens.append(data[1])
        high.append(data[2])
        low.append(data[3])
        close.append(data[4])
        volume.append(data[5])
        oi.append(data[6])
        st=''
        if op!=[]:
            if op[0]=='sma':
                value=ta.trend.SMAIndicator(pd.Series(close),op[1]).sma_indicator().iloc[-1]
            elif op[0]=='supertrend':
                value=pd.DataFrame(pta.supertrend(pd.Series(high),pd.Series(low),pd.Series(close),op[1],op[2]))
                if value.empty==False :
                    value=value.iloc[-1][0]
                    st=value
                    print("st: ",st)
                else:
                    value='nan'
        data.append(value)
        print("here")
        print("st: ",st)
        print("close: ",close[-1])

        if st!='' and close[-1]>st and gt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend green")
                firsttrade = 1;
                #BUYING CE
                oidentry = findStrikePriceATM("nifty", "CE")

            else:
                print('Close Greater then Supertrend. So supertrend is green. Buy CE/Sell PE and exit last position')
                #BUYING CE
                oidentry = findStrikePriceATM("nifty", "CE")
                time.sleep(1)
                #Exit PE
                oidexit = exitPosition(tradePEoption)

            gt=0
            lt=1
        elif st!='' and close[-1]<st and lt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend Red")
                firsttrade = 1;
                #BUYING PE
                oidentry = findStrikePriceATM("nifty", "PE")

            else:
                print('Close Less then Supertrend. So supertrend is red. Buy PE/Sell CE and exit last position')
                #BUYING PE
                oidentry = findStrikePriceATM("nifty", "PE")
                time.sleep(1)
                #Exit CE
                oidexit = exitPosition(tradeCEoption)
            lt=0
            gt=1
        #elif pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')) > pd.to_datetime(str(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'))+'03:15:00'):
        elif (dt1.hour >= 15 and dt1.minute >= 15):
            if lt == 0:
                print("EOD. Current open trade is based on Supertrend Red")
                #Exit Position
                oidexit = exitPosition(tradePEoption)
            elif gt == 0:
                print("EOD. Current open trade is based on Supertrend Green")
                #Exit position
                oidexit = exitPosition(tradeCEoption)
            print('End Of the Day')
            break
        print(data)


#------------Saving the final lists in csv file------------------
df_write = pd.DataFrame(columns=['opens','close','high','low'])

for i in range(0,len(opens)):
    df1 = {'opens':opens[i], 'close':close[i], 'high':high[i], 'low':low[i]}
    df_write = df_write.append(df1, ignore_index = True)

df_write.to_csv('lists.csv', index = False)