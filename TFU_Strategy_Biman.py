#DISCLAIMER:
#1) This sample code is for learning purposes only.
#2) Always be very careful when dealing with codes in which you can place orders in your account.
#3) The actual results may or may not be similar to backtested results. The historical results do not guarantee any profits or losses in the future.
#4) You are responsible for any losses/profits that occur in your account in case you plan to take trades in your account.
#5) TFU and Aseem Singhal do not take any responsibility of you running these codes on your account and the corresponding profits and losses that might occur.

from kiteconnect import KiteConnect
import datetime
import time
import threading
import pandas as pd
import requests

####################__INPUT__#####################
api_key = ""  #7ou6sfi096xoffjf
access_token = ""
kc = KiteConnect(api_key=api_key)
kc.set_access_token(access_token)

#TIME TO FIND THE STRIKE
entryHour   = 0
entryMinute = 0
entrySecond = 0


stock="NIFTY" # BANKNIFTY OR NIFTY
stock_level = 18000
otm = 300  #If you put -100, that means its 100 points ITM.
SL_point = 0
Target_point = 0
reverse_sl_point = 0
reverse_target_point = 0
PnL = 0
premium = 80
option_level = 100
choiceCallPut = "CE"
df = pd.DataFrame(columns=['Date','CE_Entry_Price','CE_Exit_Price','PE_Entry_Price','PE_Exit_Price','PnL'])
df["Date"] = [datetime.date.today()]


expiry = {
    "year": "23",
    "month": "1",
    "day": "05"
}

clients = [
    {
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
        name = "NSE:"+"NIFTY BANK"   #"NSE:NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #22D22

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)
    print(ltp)

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
    elif stock== "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if choiceCallPut=="CE":
        takeEntry(closest_Strike_CE, atmCE)
    else:
        takeEntry(closest_Strike_PE, atmPE)

def findStrikePriceATM_reverse():
    print(" Placing Orders ")
    global kc
    global clients
    global SL_percentage

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"   #"NSE:NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY 50"       #"NSE:NIFTY 50"
    #TO get feed to Nifty: "NSE:NIFTY 50" and banknifty: "NSE: NIFTY BANK"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]   #22D22

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)
    print(ltp)

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
    elif stock== "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if choiceCallPut=="CE":
        takeEntry_reverse(closest_Strike_PE, atmPE)
    else:
        takeEntry_reverse(closest_Strike_CE, atmCE)

def findStrikePricePremium():
    print(" Placing Orders ")
    global kc
    global clients
    global SL_percentage
    global premium

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"
    elif stock=="NIFTY":
        name = "NSE:"+stock+" 50"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)                  #ltp = kc.ltp([name])[name]['last_price']
    if stock == "BANKNIFTY":
        for i in range(-8, 8):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
        print(strikeList)

        #FOR CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:BANKNIFTY" + str(intExpiry)+str(strike)+"CE")
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_CE = strike
                prev_diff = diff
            #time.sleep(.5)

        #FOR PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:BANKNIFTY" + str(intExpiry)+str(strike)+"PE")
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_PE = strike
                prev_diff = diff
           # time.sleep(.5)


    elif stock == "NIFTY":
        for i in range(-5, 5):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
            strikeList.append(strike+50)
        print(strikeList)

        #For CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:NIFTY" + str(intExpiry)+str(strike)+"CE")
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_CE=strike
                prev_diff=diff
           # time.sleep(.5)

        #For PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:NIFTY" + str(intExpiry)+str(strike)+"PE")
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_PE=strike
                prev_diff=diff
           # time.sleep(.5)

    print("closest CE",closest_Strike_CE)
    print("closest PE",closest_Strike_PE)

    if stock == "BANKNIFTY":
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif stock == "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if choiceCallPut=="CE":
        takeEntry(closest_Strike_CE, atmCE)
    else:
        takeEntry(closest_Strike_PE, atmPE)

def findStrikePricePremium_reverse():
    print(" Placing Orders ")
    global kc
    global clients
    global SL_percentage
    global premium

    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"
    elif stock=="NIFTY":
        name = "NSE:"+stock+" 50"

    strikeList=[]

    prev_diff = 10000
    closest_Strike=10000

    intExpiry=expiry["year"]+expiry["month"]+expiry["day"]

    ######################################################
    #FINDING ATM
    ltp = getLTP(name)                  #ltp = kc.ltp([name])[name]['last_price']
    if stock == "BANKNIFTY":
        for i in range(-8, 8):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
        print(strikeList)

        #FOR CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:BANKNIFTY" + str(intExpiry)+str(strike)+"CE")
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_CE = strike
                prev_diff = diff
            #time.sleep(.5)

        #FOR PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:BANKNIFTY" + str(intExpiry)+str(strike)+"PE")
            diff = abs(ltp_option - premium)
            print("diff==>", diff)
            if (diff < prev_diff):
                closest_Strike_PE = strike
                prev_diff = diff
        # time.sleep(.5)


    elif stock == "NIFTY":
        for i in range(-5, 5):
            strike = (int(ltp / 100) + i) * 100
            strikeList.append(strike)
            strikeList.append(strike+50)
        print(strikeList)

        #For CE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:NIFTY" + str(intExpiry)+str(strike)+"CE")
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_CE=strike
                prev_diff=diff
        # time.sleep(.5)

        #For PE
        prev_diff = 10000
        for strike in strikeList:
            ltp_option = getLTP("NFO:NIFTY" + str(intExpiry)+str(strike)+"PE")
            diff = abs(ltp_option - premium)
            print("diff==>",diff)
            if (diff < prev_diff):
                closest_Strike_PE=strike
                prev_diff=diff
        # time.sleep(.5)

    print("closest CE",closest_Strike_CE)
    print("closest PE",closest_Strike_PE)

    if stock == "BANKNIFTY":
        atmCE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:BANKNIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"
    elif stock == "NIFTY":
        atmCE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_CE)+"CE"
        atmPE = "NFO:NIFTY" + str(intExpiry)+str(closest_Strike_PE)+"PE"

    print(atmCE)
    print(atmPE)

    if choiceCallPut=="CE":
        takeEntry_reverse(closest_Strike_PE, atmPE)
    else:
        takeEntry_reverse(closest_Strike_CE, atmCE)


def takeEntry(closest_Strike_CE, atmCE):
    global SL_point
    global PnL

    #check for option level
    x = 1
    while x == 1:
        dt = datetime.datetime.now()
        ltp = getLTP(atmCE)
        if (ltp <= option_level):
            print("option price reached")
            x = 2
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new option price ")

    ce_entry_price = getLTP(atmCE)
    PnL = ce_entry_price
    print("Current PnL is: ", PnL)
    df['CE_Entry_Price'] = [ce_entry_price]

    print(" closest_CE ATM ", closest_Strike_CE, " CE Entry Price = ", ce_entry_price)

    ceSL = round(ce_entry_price + SL_point, 1)
    ceTarget = round(ce_entry_price - Target_point, 1)
    print("Placing Order CE Entry Price = ", ce_entry_price, "|  CE SL => ", ceSL)

    #SELL AT MARKET PRICE
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        qty = client['qty']
        oidentryCE = 0
        oidentryCE = placeOrderSingle( atmCE, "SELL", qty, "MARKET", ce_entry_price, "regular")
        print("The OID of Entry CE is: ", oidentryCE)

    exitPosition(atmCE, ceSL, ce_entry_price, ceTarget, qty)


def takeEntry_reverse(closest_Strike_CE, atmCE):
    global SL_point
    global PnL

    ce_entry_price = getLTP(atmCE)

    print(" closest_CE ATM ", closest_Strike_CE, " CE Entry Price = ", ce_entry_price)

    ceSL = round(ce_entry_price + reverse_sl_point, 1)
    ceTarget = round(ce_entry_price - reverse_target_point, 1)
    print("Placing Order CE Entry Price = ", ce_entry_price, "|  CE SL => ", ceSL)

    #SELL AT MARKET PRICE
    for client in clients:
        print("\n============_Placing_Trades_=====================")
        qty = client['qty']
        oidentryCE = 0
        oidentryCE = placeOrderSingle( atmCE, "SELL", qty, "MARKET", ce_entry_price, "regular")
        print("The OID of Entry CE is: ", oidentryCE)

    exitPosition_reverse(atmCE, ceSL, ce_entry_price, ceTarget, qty)

def exitPosition(atmCE, ceSL, ce_entry_price, ceTarget, qty):
    global PnL
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = getLTP(atmCE)
            #Target Hit
            if ((ltp <= ceTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "Close"
                print("All trades done. Exiting Code")
            #SL Hit
            elif (ltp > ceSL) and ltp != -1:
                oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "SL"
                findStrikePriceATM_reverse()
            else:
                print("NO SL is hit")
                time.sleep(1)

        except:
            print("Couldn't find LTP , RETRYING !!")
            time.sleep(1)

def exitPosition_reverse(atmCE, ceSL, ce_entry_price, ceTarget, qty):
    global PnL
    traded = "No"

    while traded == "No":
        dt = datetime.datetime.now()
        try:
            ltp = getLTP(atmCE)
            #Target Hit
            if ((ltp <= ceTarget) or (dt.hour >= 15 and dt.minute >= 15)) and ltp != -1:
                oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "Close"
                print("All trades done. Exiting Code")
            #SL Hit
            elif (ltp > ceSL) and ltp != -1:
                oidexitCE = placeOrderSingle( atmCE, "BUY", qty, "MARKET", ceSL, "regular")
                print("The OID of Exit CE is: ", oidexitCE)
                traded = "Close"
                print("All trades done. Exiting Code")
            else:
                print("NO SL is hit")
                time.sleep(1)

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


def wait_for_level():
    x = 1
    if stock == "BANKNIFTY":
        name = "NSE:"+"NIFTY BANK"   #"NSE:NIFTY BANK"
    elif stock == "NIFTY":
        name = "NSE:"+"NIFTY 50"       #"NSE:NIFTY 50"

    while x == 1:
        dt = datetime.datetime.now()
        ltp = getLTP(name)
        if (ltp >= stock_level):
            print("price reached")
            x = 2
            findStrikePriceATM()
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new stock price ")


def checkTime_tofindStrike():
    x = 1
    while x == 1:
        dt = datetime.datetime.now()
        if( dt.hour >= entryHour and dt.minute >= entryMinute and dt.second >= entrySecond ):
            print("time reached")
            x = 2
            wait_for_level()
        else:
            time.sleep(.1)
            print(dt , " Waiting for Time to check new ATM ")


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
df["PnL"] = [PnL]
df.to_csv('Str1.csv',mode='a',index=True,header=True)