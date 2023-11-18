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
import pandas as pd
import requests

####################__INPUT__#####################
api_key = open("zerodha_api_key.txt",'r').read()
access_token = open("zerodha_access_token.txt",'r').read()
kc = KiteConnect(api_key=api_key)
kc.set_access_token(access_token)

#TIME TO FIND THE STRIKE
entryHour   = 0
entryMinute = 0
entrySecond = 0
startTime = datetime.time(entryHour, entryMinute, entrySecond)


stock="NIFTY" # BANKNIFTY OR NIFTY
otm = 500
SL_percentage = 0
target_percentage = 0
PnL = 0
df = pd.DataFrame(columns=['Date','CE_Entry_Price','CE_Exit_Price','PE_Entry_Price','PE_Exit_Price','PnL'])
df["Date"] = [datetime.date.today()]

expiry ={
    "year": "23",
    "month": "6",
    "day": "08",
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


def findStrikePriceATM():
    print(" Placing Orders ")
    global kc
    global clients
    global SL_percentage

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+stock+" 50"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)                  #ltp = kc.ltp([name])[name]['last_price']
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

    takeEntry(closest_Strike_CE, closest_Strike_PE, atmCE, atmPE)



def takeEntry(closest_Strike_CE, closest_Strike_PE, atmCE, atmPE):
    global SL_percentage
    global target_percentage
    global PnL

    ce_entry_price = getLTP(atmCE)
    pe_entry_price = getLTP(atmPE)
    PnL = ce_entry_price + pe_entry_price
    print("Current PnL is: ", PnL)
    df["CE_Entry_Price"] = [ce_entry_price]
    df["PE_Entry_Price"] = [pe_entry_price]

    print(" closest_CE ATM ", closest_Strike_CE, " CE Entry Price = ", ce_entry_price)
    print(" closest_PE ATM", closest_Strike_PE, " PE Entry Price = ", pe_entry_price)

    ceSL = round(ce_entry_price * (1 + SL_percentage / 100), 1)
    peSL = round(pe_entry_price * (1 + SL_percentage / 100), 1)
    ceTarget = round(ce_entry_price * (1 - target_percentage / 100), 1)
    peTarget = round(pe_entry_price * (1 - target_percentage / 100), 1)
    print("Placing Order CE Entry Price = ", ce_entry_price, "|  CE SL => ", ceSL, "| CE Target => ", ceTarget)
    print("Placing Order PE Entry Price = ", pe_entry_price, "|  PE SL => ", peSL, "| PE Target => ", peTarget)

    #SELL AT MARKET PRICE
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        print("userID = ", client['userID'])
        broker = client['broker']
        uid = client['userID']
        key = client['apiKey']
        token = client['accessToken']
        qty = client['qty']

        oidentryCE = placeOrderSingle( atmCE, "SELL", qty, "MARKET", ce_entry_price, "regular")
        oidentryPE = placeOrderSingle( atmPE, "SELL", qty, "MARKET", pe_entry_price, "regular")
        print("The OID of Entry CE is: ", oidentryCE)
        print("The OID of Entry PE is: ", oidentryPE)

        exitPosition(atmCE, ceSL, ceTarget, ce_entry_price, atmPE, peSL, peTarget, pe_entry_price, qty)


def exitPosition(atmCE, ceSL, ceTarget, ce_entry_price, atmPE, peSL, peTarget, pe_entry_price, qty):
    global PnL
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = getLTP(atmCE)
            ltp1 = getLTP(atmPE)
            if ((ltp > ceSL) or (ltp < ceTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                PnL = PnL - ltp
                print("Current PnL is: ", PnL)
                df["CE_Exit_Price"] = [ltp]
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "CE"
            elif ((ltp1 > peSL) or (ltp1 < peTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp1 != -1:
                oidexitPE = placeOrderSingle( atmPE, "BUY", qty, "MARKET", peSL, "regular")
                PnL = PnL - ltp1
                print("Current PnL is: ", PnL)
                df["PE_Exit_Price"] = [ltp1]
                print("The OID of Exit PE is: ", oidexitPE)
                traded = "PE"
            else:
                print("PE SL and Target not hit")
                time.sleep(1)

        except:
            print("Couldn't find LTP , RETRYING !!")
            time.sleep(1)

    if (traded == "CE"):
        peSL = pe_entry_price
        while traded == "CE":
            dt = datetime.datetime.now()
            try:
                ltp = getLTP(atmPE)
                if ((ltp > peSL) or (ltp < peTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitPE = placeOrderSingle( atmPE, "BUY", qty, "MARKET", peSL, "regular")
                    PnL = PnL - ltp
                    print("Current PnL is: ", PnL)
                    df["PE_Exit_Price"] = [ltp]
                    print("The OID of Exit PE is: ", oidexitPE)
                    traded = "Close"
                else:
                    print("PE SL and Target not hit")
                    time.sleep(1)

            except:
                print("Couldn't find LTP , RETRYING !!")
                time.sleep(1)

    elif (traded == "PE"):
        ceSL = ce_entry_price
        while traded == "PE":
            dt = datetime.datetime.now()
            try:
                ltp = getLTP(atmCE)
                if ((ltp > ceSL) or (ltp < ceTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                    oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                    PnL = PnL - ltp
                    df["CE_Exit_Price"] = [ltp]
                    print("Current PnL is: ", PnL)
                    print("The OID of Exit CE is: ", oidexitCE)
                    traded = "Close"
                else:
                    print("CE SL and Target not hit")
                    time.sleep(1)
            except:
                print("Couldn't find LTP , RETRYING !!")
                time.sleep(1)

    elif (traded == "Close"):
        print("All trades done. Exiting Code")


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
            findStrikePriceATM()
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new ATM ")


def placeOrderSingle(inst ,t_type,qty,order_type,price,variety):
    exch = inst[:3]
    symb = inst[4:]
    papertrading = 0 #if this is 1, then real trades will be placed
    dt = datetime.datetime.now()
    print(dt.hour,":",dt.minute,":",dt.second ," => ",t_type," ",symb," ",qty," ",order_type)
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
df["PnL"] = [PnL]
df.to_csv('Str2.csv',mode='a',index=True,header=True)