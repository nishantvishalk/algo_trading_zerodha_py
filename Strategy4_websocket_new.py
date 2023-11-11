#DISCLAIMER:
#1) This sample code is for learning purposes only.
#2) Always be very careful when dealing with codes in which you can place orders in your account.
#3) The actual results may or may not be similar to backtested results. The historical results do not guarantee any profits or losses in the future.
#4) You are responsible for any losses/profits that occur in your account in case you plan to take trades in your account.
#5) TFU and Aseem Singhal do not take any responsibility of you running these codes on your account and the corresponding profits and losses that might occur.
#6) The running of the code properly is dependent on a lot of factors such as internet, broker, what changes you have made, etc. So it is always better to keep checking the trades as technology error can come anytime.
#7) This is NOT a tip providing service/code.
#8) This is NOT a software. Its a tool that works as per the inputs given by you.
#9) Slippage is dependent on market conditions.
#10) Option trading and automatic API trading are subject to market risks

#https://buildmedia.readthedocs.org/media/pdf/technical-analysis-library-in-python/latest/technical-analysis-library-in-python.pdf


import time

from kiteconnect import KiteConnect
from datetime import datetime,timedelta
from pytz import timezone
import ta    # Python TA Lib
import pandas as pd
import pandas_ta as pta    # Pandas TA Libv
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def getHistorical(ticker,interval,duration, instrument_df):
    range_from = datetime.today()-timedelta(duration)
    range_to = datetime.today()
    symb = ticker[4:]

    if interval == 1:
        interval_str = "minute"
    elif interval == 3:
        interval_str = "3minute"
    elif interval == 5:
        interval_str = "5minute"
    elif interval == 10:
        interval_str = "10minute"
    elif interval == 15:
        interval_str = "15minute"
    elif interval == 30:
        interval_str = "30minute"
    elif interval == 60:
        interval_str = "60minute"


    instrument = instrument_df[instrument_df.tradingsymbol==symb].instrument_token.values[0]
    data = pd.DataFrame(kc.historical_data(instrument,range_from, range_to,interval_str))
    data.set_index("date",inplace=True)
    filtered_df = data[data.index.time < pd.to_datetime('15:30:00').time()]
    return filtered_df




def getLTP(instrument):
    url = "http://localhost:4000/ltp?instrument=" + instrument

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    data = resp.json()
    return data


def findStrikePriceATM(stock, cepe):
    global tradeCEoption
    global tradePEoption
    print(" Finding ATM ")
    global kc
    global clients
    global SL_percentage

    if (stock == "BANKNIFTY"):
        name = "NSE:"+"NIFTY BANK"   #"NSE:NIFTY BANK"
    elif (stock == "NIFTY"):
        name = "NSE:"+"NIFTY 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #22OCT

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)

    if stock == "BANKNIFTY":
        closest_Strike = int(round((ltp / 100),0) * 100)
        print(closest_Strike)


    elif stock == "NIFTY":
        closest_Strike = int(round((ltp / 50),0) * 50)
        print(closest_Strike)

    print("closest",closest_Strike)
    closest_Strike_CE = closest_Strike+otm
    closest_Strike_PE = closest_Strike-otm

    if (stock == "BANKNIFTY"):
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif (stock == "NIFTY"):
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
    global tradesDF
    exch = inst[:3]
    symb = inst[4:]
    papertrading = 0 #if this is 1, then real trades will be placed
    dt = datetime.now()
    print(dt.hour,":",dt.minute,":",dt.second ," => ",t_type," ",symb," ",qty," ",order_type," @ price =  ",price)
    try:

        trade_price = getLTP(inst)
        tradesDF = tradesDF._append(pd.Series([dt.date(), dt.time(), symb, t_type, trade_price], index=tradesDF.columns), ignore_index=True)

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

api_key = "7ou6sfi096xoffjf"
access_token = "15ttD2Ag6R30unIiocvtyLOl98OLxewi"
kc = KiteConnect(api_key=api_key)
kc.set_access_token(access_token)

checkInstrument = "NSE:NIFTY 50"
stock = "NIFTY"
timeFrame = 1
tradeCEoption = ""
tradePEoption = ""

instrument_dump = kc.instruments(checkInstrument[:3])
instrument_df = pd.DataFrame(instrument_dump)
print(instrument_df)

# order's details dataframe
tradesDF = pd.DataFrame(columns=["Date", "Entry/Exit Time", "Symbol", "Direction", "Entry/Exit Price"])

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
    "year": "23",
    "month": "6",
    "day": "08",
}
otm = 0

x = 1
close=[]   #close[17873, 17777, 17772]
opens=[]
high=[]
low=[]
ttime = []


op=['supertrend',1,1]
print(['datetime','open','high','low','close'])
gt=1
lt=1
xx = 2
firsttrade = 0
maxtrade = 0
st = ""


while x == 1:
    dt1 = datetime.now()

    #Find OHLC at the end of the timeframe
    if dt1.second <= 1 and dt1.minute % timeFrame == 0:
        data=getHistorical(checkInstrument,timeFrame,5, instrument_df)  #(instrument name, timeframe, number of days)
        print(dt1)
        print(data)
        opens = data['open'].to_numpy()
        high = data['high'].to_numpy()
        low = data['low'].to_numpy()
        close = data['close'].to_numpy()
        volume = data['volume'].to_numpy()
        #ttime = data['date']

        st=''
        if op!=[]:
            if op[0]=='sma':
                value=ta.trend.SMAIndicator(pd.Series(close),op[1],False).sma_indicator().iloc[-1]
                #psar = ta.trend.PSARIndicator(pd.Series(high), pd.Series(low), pd.Series(close), 0.02, 0.2, False).psar().iloc[-1]
                #adx = ta.trend.ADXIndicator(pd.Series(high), pd.Series(low), pd.Series(close), op[1], False).adx().iloc[-1]
            elif op[0]=='supertrend':
                value=pd.DataFrame(pta.supertrend(pd.Series(high),pd.Series(low),pd.Series(close),op[1],op[2]))
                if value.empty==False :
                    value=value.iloc[-1][0]
                    st=value
                    print("st: ",st)
                else:
                    value='nan'
        time.sleep(1)
    else:
        if st!='' and close[-1]>st and gt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend green")
                firsttrade = 1;
                #BUYING CE
                oidentry = findStrikePriceATM("NIFTY", "CE")

            else:
                print('Close Greater then Supertrend. So supertrend is green. Buy CE/Sell PE and exit last position')
                #Exit PE
                oidexit = exitPosition(tradePEoption)
                time.sleep(1)
                #BUYING CE
                oidentry = findStrikePriceATM("NIFTY", "CE")

            gt=0
            lt=1
        elif st!='' and close[-1]<st and lt==1 and st!='nan':
            if firsttrade == 0:
                print("This is the first trade. Supertrend Red")
                firsttrade = 1;
                #BUYING PE
                oidentry = findStrikePriceATM("NIFTY", "PE")

            else:
                print('Close Less then Supertrend. So supertrend is red. Buy PE/Sell CE and exit last position')
                #Exit CE
                oidexit = exitPosition(tradeCEoption)
                time.sleep(1)
                #BUYING PE
                oidentry = findStrikePriceATM("NIFTY", "PE")
            lt=0
            gt=1
        #elif pd.to_datetime(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d %H:%M:%S')) > pd.to_datetime(str(datetime.now(timezone("Asia/Kolkata")).strftime('%Y-%m-%d'))+'03:15:00'):
        if (dt1.hour >= 15 and dt1.minute >= 5):
            if lt == 0:
                print("EOD. Current open trade is based on Supertrend Red")
                #Exit Position
                oidexit = exitPosition(tradePEoption)
            elif gt == 0:
                print("EOD. Current open trade is based on Supertrend Green")
                #Exit position
                oidexit = exitPosition(tradeCEoption)
            print('End Of the Day')
            x = 2
            break

#------------Saving the final lists in csv file------------------
tradesDF.to_csv("st4_zerodha.csv")


