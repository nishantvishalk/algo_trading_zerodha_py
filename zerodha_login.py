# -----------------------------------------------------------------------------------#
# 1. Manual Login
# 2. Automatic Login using Selenium
# -----------------------------------------------------------------------------------#

# Import the required Libraries
from kiteconnect import KiteConnect
from pprint import pprint
import logging
from kiteconnect import KiteTicker
import pandas
import keys_cred

#  Set your Account Details Here
# api_key = "j1qak21f8a5zqwzh"
# secret_key = "c4l9osval7f1nokyfzj807vlsf0eiyo9"
# access_token = "rK0Xg2Hya1drbU3Xdzh3g7MSP82wdPho"

#microsoft visual C++ installed.
#pip install KiteConnect
#pip install Twisted

kite = KiteConnect(api_key=keys_cred.api_key)

def manualLogin():
    global access_token, kite

    print(" Visit URL , Enter Details and get RequestToken :")
    login_url = "https://kite.trade/connect/login?api_key=" + keys_cred.api_key
    print(login_url)

    code = input("Enter RedirectURI token ")

    data = kite.generate_session(code, api_secret=keys_cred.secret_key)
    kite.set_access_token(data["access_token"])

    accessToken = data["access_token"]
    print("Access Token = ", accessToken)
    access_token = accessToken
    kite.set_access_token(access_token)


manualLogin()


