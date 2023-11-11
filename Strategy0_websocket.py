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

from kiteconnect import KiteConnect
import datetime
import time
import requests

######PIVOT POINTS##########################
####################__INPUT__#####################
isEnd = False
api_key = ""
access_token = ""


kc = KiteConnect(api_key=api_key)
kc.set_access_token(access_token)

#TIME TO FIND THE STRIKE
entryHour   = 0
entryMinute = 0
entrySecond = 0
startTime = datetime.time(entryHour, entryMinute, entrySecond)

stock="NIFTY" # BANKNIFTY OR NIFTY
otm = 500  #If you put -100, that means its 100 points ITM.
SL_percentage = 0.4
target_percentage = 1.2
yesterday_closing_price = 17530


expiry ={
    "year": "23",
    "month": "6",
    "day": "08",
    #YYMDD  22O06  22OCT
}
clients = [
    {
        "broker": "zerodha",
        "userID": "US3111",
        "apiKey": "",
        "accessToken": "",
        "qty" : 50
    }
]


##################################################


def findStrikePriceATM(cepe, sl_fut, target_fut):
    global kc
    global clients
    global SL_percentage

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #22SEP

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

    if stock == "BANKNIFTY":
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif stock == "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if cepe == "CE":
        takeEntry(closest_Strike_CE, atmCE, sl_fut, target_fut, name, cepe)
    else:
        takeEntry(closest_Strike_PE, atmPE, sl_fut, target_fut, name, cepe)


def takeEntry(closest_Strike, atmCEPE, sl_fut, target_fut, name, cepe):
    global SL_point
    cepe_entry_price = getLTP(atmCEPE)
    print(" closest ATM ", closest_Strike, " CE/PE Entry Price = ", cepe_entry_price)

    #SELL AT MARKET PRICE
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']

        #oidentryCE = 0
        #oidentryPE = 0

        oidentry = placeOrderSingle( atmCEPE, "SELL", qty, "MARKET", cepe_entry_price, "regular")

        print("The OID of Entry is: ", oidentry)
        exitPosition(atmCEPE, sl_fut, target_fut, qty, name, cepe)


def exitPosition(atmCEPE, sl_fut, target_fut, qty, name, cepe):
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = getLTP(name)

            #if LTP (Nifty) < s1, then we are going to sell CE. Future = SELL
            if (cepe == "CE"):
                if ((ltp < target_fut) or (ltp > sl_fut) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderSingle( atmCEPE, "BUY", qty, "MARKET", 0, "regular")
                    print("The OID of Exit is: ", oidexitCE)
                    traded = "Close"
                else:
                    time.sleep(1)
            #if LTP (Nifty) > r1, then I am going to Sell PE. Future = LONG / BUY
            else:
                if ((ltp > target_fut) or (ltp < sl_fut) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderSingle( atmCEPE, "BUY", qty, "MARKET", 0, "regular")
                    print("The OID of Exit is: ", oidexitCE)
                    traded = "Close"
                else:
                    time.sleep(1)
            time.sleep(30)

        except:
            print("Couldn't find LTP , RETRYING !!")
            time.sleep(1)



def getLTP(instrument):
    url = "http://localhost:4000/ltp?instrument=" + instrument
    try:
        resp = requests.get(url)
    except Exception as e:
        print(e)
    data = resp.json()
    return data



def checkTime_tofindStrike():
    x = 1
    while x == 1:
        dt = datetime.datetime.now()
        #if( dt.hour >= entryHour and dt.minute >= entryMinute and dt.second >= entrySecond ):
        if (dt.time() >= startTime):
            print("time reached")
            x = 2
            while not isEnd:
                takeEntryFut()
                time.sleep(1)
            #findStrikePriceATM()
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new ATM ")


def takeEntryFut():
    global isEnd
    global kc
    global clients
    global SL_percentage
    global target_percentage

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"
        yesterdayHigh = 37638
        yesterdayLow = 37291
        yesterdayClose = 37335
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY 50"
        yesterdayHigh = 17176.45
        yesterdayLow = 16942.35
        yesterdayClose = 17007.4

    time=datetime.datetime.now()
    minute = time.strftime("%M")
    second = time.strftime("%S")

    pp = (yesterdayHigh + yesterdayLow + yesterdayClose)/3
    r1 = (pp * 2) - yesterdayLow
    s1 = (pp * 2) - yesterdayHigh
    print(r1)
    print(s1)

    if int(minute)%5 ==0 and int(second) ==0 :
        print("This is every fifth minute", minute)
        ltp = getLTP(name)

        if ltp > r1:
            sl_fut = round(ltp*(1-SL_percentage/100),1)
            target_fut = round(ltp*(1+target_percentage/100),1)
            print("here")
            findStrikePriceATM("PE", sl_fut, target_fut)
            print("here2")
            isEnd = True
        elif ltp < s1:
            sl_fut = round(ltp*(1+SL_percentage/100),1)
            target_fut = round(ltp*(1-target_percentage/100),1)
            print("here")
            findStrikePriceATM("CE", sl_fut, target_fut)
            print("here2")
            isEnd = True


def placeOrderSingle(inst ,t_type,qty,order_type,price,variety):
    exch = inst[:3]
    symb = inst[4:]
    papertrading = 0 #if this is 1, then real trades will be placed
    dt = datetime.datetime.now()
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



checkTime_tofindStrike()