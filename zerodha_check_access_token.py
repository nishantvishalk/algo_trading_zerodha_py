from kiteconnect import KiteConnect

apiKey = ""
accessToken = ""
kc = KiteConnect(api_key=apiKey)
kc.set_access_token(accessToken)

userid = kc.profile()
print(userid)
