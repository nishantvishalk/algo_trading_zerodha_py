from urllib import response
from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
from pprint import pprint
import threading
from flask import Flask, request

##############################################
#                   INPUT's                  #
##############################################
apiKey = open("zerodha_api_key.txt",'r').read()
accessToken = open("zerodha_access_token.txt",'r').read()
kc = KiteConnect(api_key=apiKey)
kc.set_access_token(accessToken)

expiry = {
    "year": "23",
    "month": "N",
    "day": "16"
    #For monthly it will be year = "23", month = "SEP", day = ""
}

expiry_bn = {
    "year": "23",
    "month": "N",
    "day": "15"
    #For monthly it will be year = "23", month = "SEP", day = ""
}

intExpiry=expiry["year"]+expiry["month"]+expiry["day"]
intExpiry_BN = expiry_bn["year"]+expiry_bn["month"]+expiry_bn["day"]
strikeList=[]
instrumentList = []

#NIFTY
ltp = kc.quote(['NSE:NIFTY 50'])
a = ltp['NSE:NIFTY 50']['last_price']

for i in range(-5, 5):
    strike = (int(a / 100) + i) * 100
    strikeList.append(strike)
    strikeList.append(strike+50)

#Add Index
instrumentList.append('NSE:NIFTY 50')

#Add CE
for strike in strikeList:
    ltp_option = "NFO:NIFTY" + str(intExpiry)+str(strike)+"CE"
    instrumentList.append(ltp_option)

#Add PE
for strike in strikeList:
    ltp_option = "NFO:NIFTY" + str(intExpiry)+str(strike)+"PE"
    instrumentList.append(ltp_option)

strikeList=[]
#BANKNIFTY
ltp = kc.quote(['NSE:NIFTY BANK'])
a = ltp['NSE:NIFTY BANK']['last_price']

for i in range(-10, 10):
    strike = (int(a / 100) + i) * 100
    strikeList.append(strike)

#Add Index
instrumentList.append('NSE:NIFTY BANK')

#Add CE
for strike in strikeList:
    ltp_option = "NFO:BANKNIFTY" + str(intExpiry_BN)+str(strike)+"CE"
    instrumentList.append(ltp_option)

#Add PE
for strike in strikeList:
    ltp_option = "NFO:BANKNIFTY" + str(intExpiry_BN)+str(strike)+"PE"
    instrumentList.append(ltp_option)


instrumentList1 = [
    "NSE:ABFRL",
    "NSE:ADANIENT",
    "NSE:ADANIPORTS",
    "NSE:ABB",
    "NSE:INFY",
    "NSE:NIFTY 50",
    "NFO:NIFTY23NOVFUT"
]

instrumentList = instrumentList + instrumentList1
print("BELOW IS THE COMPLETE INSTRUMENT LIST")
print(instrumentList)
##############################################
print("!! Started getltpDict.py !!")

app = Flask(__name__)


tokenMapping = { }
ltpDict = { }

@app.route('/')
def hello_world():
	return 'Hello World'

@app.route('/ltp')
def getLtp():
    global ltpDict
    print(ltpDict)
    ltp = -1
    instrumet = request.args.get('instrument')
    try:
        ltp = ltpDict[instrumet]
    except Exception as e :
        print("EXCEPTION occured while getting ltpDict()")
        print(e)
    return str(ltp)



def getTokensList(instrumentList):
    global tokenMapping
    response = kc.ltp(instrumentList)
    tokensList = []
    for inst in instrumentList:
        token = response[inst]['instrument_token']
        tokensList.append(token)
        tokenMapping[token] = inst
    return tokensList

def on_ticks(ws, ticks):
    global ltpDict
    for tick in ticks:
        inst = tokenMapping[tick['instrument_token']]
        ltpDict[inst] = tick['last_price']
    print(ltpDict)

def on_connect(ws, response):
    global instrumentList
    tokensList = getTokensList(instrumentList)
    ws.subscribe(tokensList)
    ws.set_mode(ws.MODE_LTP,  tokensList)

def on_close(ws, code, reason):
    # On connection close stop the main loop
    # Reconnection will not happen after executing `ws.stop()`
    ws.stop()

def startServer():
    print("Inside startServer()")
    app.run(host='0.0.0.0', port=4000)

def main():
    print("Inside main()")
    t1 = threading.Thread(target=startServer)
    t1.start()
    
    kws = KiteTicker(apiKey , accessToken)
    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_close = on_close
    kws.connect()
    t1.join()
    print("websocket started !!")

main()