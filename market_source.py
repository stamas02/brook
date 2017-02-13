import requests
import json
import hmac
import hashlib
from sseclient import SSEClient
from urllib import quote
import math
import base64
import time
import datetime
import numpy as np
import threading

class MarketSource:
    def __init__(self):
        pass


class Plus500(MarketSource):
    def __init__(self, instrument, verbose = 0):
        self._instruments={
            "cat3_sc2": {
                "Bitcoin" : 2274
            },
            "cat3_sc1":{
                "AUD/CAD": 384
                },
            "cat3_sc0":{
                "GBP/USD": 28,
                "EUR/USD": 2,
                "GBP/AUD": 378
            }
        }
        self._instrument_name = instrument
        self._instrument_index = self._instrument_index(self._instrument_name)
        self._history = {}
        self._history[self._instrument_index["Id"]] = []
        self._current_rate = None
        self.ballance = 0


        self.verbose = verbose
        self.current_milli_time = lambda: int(round(time.time() * 1000))
        self._session = requests.Session()
        self._validation_data = self._login(session=self._session,
                                            username="stamas01@gmail.com",
                                            password="Akb88FePSA")
        self._history[self._instrument_index["Id"]] = self._get_history(session=self._session,
                                                                  validation_data = self._validation_data,
                                                                  instrument_id = str(self._instrument_index["Id"]),
                                                                  resolution = 1)
        self.connect_event_stream(self._session,self._validation_data, self._instrument_index["Category"])
        return

    def get_history(self, last_n):
        if len(self._history[self._instrument_index["Id"]]) < last_n:
            return None
        return np.array(self._history[self._instrument_index["Id"]])[-last_n:]

    def _instrument_index(self, instrument_name):
        for category in self._instruments.keys():
            for name in self._instruments[category].keys():
                if name == instrument_name:
                    return {"Category" : category,"Id" : self._instruments[category][name]}
        return None

    def connect_event_stream(self,session, validation_data, instrument_category):

        # get connection token from the server
        get_params = {'clientProtocol':"1.5",
                      'UserSessionId': str(validation_data["LoginSessionID"]),
                      'WebTraderServiceId': str(validation_data["WebTraderServiceId"]),
                      'connectionData': '[{"name":"instrumentscomet"}]',
                      '_':str(self.current_milli_time)}
        url1 = "https://instrumentsfe.plus500.com/signalr/hubs/negotiate"
        connection_data = json.loads(session.get(url1,params=get_params).text)

        # Connect to the server
        url2 = "https://instrumentsfe.plus500.com/signalr/hubs/connect?" \
               "transport=serverSentEvents&" \
               "clientProtocol=1.5&" \
               "UserSessionId="+str(validation_data["LoginSessionID"])+"&" \
               "WebTraderServiceId="+str(validation_data["WebTraderServiceId"])+"&" \
               "connectionToken="+quote(str(connection_data["ConnectionToken"]))+"&" \
               "connectionData=%5B%7B%22name%22%3A%22instrumentscomet%22%7D%5D&" \
               "tid=5"
        messages = SSEClient(url2,session=session)

        # start the server
        url3 = "https://instrumentsfe.plus500.com/signalr/hubs/start?" \
               "transport=serverSentEvents&" \
               "clientProtocol=1.5&" \
               "UserSessionId="+str(validation_data["LoginSessionID"])+"&" \
               "WebTraderServiceId="+str(validation_data["WebTraderServiceId"])+"&" \
               "connectionToken="+quote(str(connection_data["ConnectionToken"]))+"&" \
               "connectionData=%5B%7B%22name%22%3A%22instrumentscomet%22%7D%5D&" \
               "_="+str(self.current_milli_time)
        _ = session.get(url3)

        # Enable dataflow
        form_data = {'Enable': "true",
                      'SessionID': str(validation_data["SessionID"]),
                      'SubSessionID': str(validation_data["SubSessionID"])}
        url4 = "https://trade.plus500.com/ClientRequest/SessionFeedControlImm"
        _ = session.post(url4, form_data)

        # Choose instrument
        form_data = {'SpecificCategory': str(instrument_category),
                      'SessionID': str(validation_data["SessionID"]),
                      'SubSessionID': str(validation_data["SubSessionID"])}
        url4 = "https://trade.plus500.com/ClientRequest/GetTradeInstruments"
        _ = session.post(url4, form_data)
        # read messages

        t = threading.Thread(target=self._receive_message, args=(messages,))
        t.daemon = True
        t.start()

    def _receive_message(self, messages):
        for msg in messages:
            try:
                timestamp_now = datetime.datetime.now()
                update = json.loads(str(msg))
                insrumentID = update["M"][0]["A"][0][0]["Feeds"][0]["InstrumentID"]
                sellRate = update["M"][0]["A"][0][0]["Feeds"][0]["SellRate"]
                buyRate = update["M"][0]["A"][0][0]["Feeds"][0]["BuyRate"]
            except:
                continue

            self._current_rate=update["M"][0]["A"][0][0]["Feeds"][0]

            timestamp_previous = datetime.datetime.fromtimestamp(self._history[insrumentID][-1,0]/1000.0)
            delta_time = timestamp_now - timestamp_previous
            if delta_time.seconds > 60:
                self._history[insrumentID].append([self._history[insrumentID][-1,0]+(60*1000),sellRate,0,0,0])

            self._history[insrumentID][2] = sellRate # Close rate
            if sellRate > self._history[insrumentID][-1][3]: #High
                self._history[insrumentID][3] = sellRate  # High
            if sellRate < self._history[insrumentID][-1][4]: #Low
                self._history[insrumentID][4] = sellRate  #Low

    def _login(self, session, username, password):
        if self.verbose == 1:
            print ("Login to plus500...")

        url1 = "https://trade.plus500.com/Login/AppStartedImm/?isInTradeContext=false"
        url2 = "https://trade.plus500.com/UserLogin/WebTrader2"
        url3 = "https://trade.plus500.com/Login/AppStartedImm/?isInTradeContext=true"
        url4 = "https://trade.plus500.com/CometAsyncHandler.ashx"
        login_data = {'userName': username,
                      'password': password,
                      'isRealMode': 'false',
                      'ClientType': "WebTrader2",
                      'machineID': "2fad5a72de4029fdb76d5b62b94a4d1a", #just a randomly generated number
                      'PrimaryMachineId': "2fad5a72de4029fdb76d5b62b94a4d1a",
                      'hl': 'en',
                      'AppVersion': '53616',
                      'SessionID': '0',
                      'SubSessionID': '0'}
        response = session.post(url1, login_data) #get key to encode the username as a sha256 hash
        login_response = json.loads(response.text)

        hash = hmac.new(str(login_response["H"]), username, hashlib.sha256).hexdigest()  # encode username
        login_data["hash"] = hash
        response = session.post(url2, login_data) # login
        validation_data = json.loads(response.text) # receive seessionIs and tokens and store it for later use

        if self.verbose == 1:
            print ("Login Result: " + str(validation_data["LoginResult"]))
        if validation_data["LoginResult"] != u'Success':
            raise "Login Failed!"


        #get html which includes the value of pageSubSessionID
        html = session.get("https://app.plus500.com/trade/majors", cookies = {'LoggedIn':'true', "IsRealMode": 'false'}).text
        ind1 = html.find("pageSubSessionID = '")+len("pageSubSessionID = '")
        ind2 = html.find("'", ind1)
        pageSubSessionID = html[ind1:ind2] # dig out the subsession id from html
        validation_data["SubSessionID"] = pageSubSessionID


        login_data = {'ClientType': "WebTrader2",
                      'machineID': "2fad5a72de4029fdb76d5b62b94a4d1a", #just a randomly generated number
                      'PrimaryMachineId': "2fad5a72de4029fdb76d5b62b94a4d1a",
                      'hl': 'en',
                      'AppVersion': '53616',
                      'refurl':'https%3A%2F%2Fapp.plus500.com%2F',
                      'SessionID': '0',
                      'SubSessionID': '0'}
        _ = session.post(url3, login_data)

        login_data = {'firstCometRequest':'true',
                      'isHttpStreamEnabled': 'false',
                      'sessID': str(validation_data["SessionID"]),
                      'subSessID': str(validation_data["SubSessionID"])}
        _ = session.post(url4, login_data)
        if self.verbose == 1:
            print (_.text)
        return validation_data

    def _get_history(self, session, validation_data, instrument_id, resolution):
        get_params = {'InstrumentID':str(instrument_id),
                      'FeedResolutionLevel': str(resolution),
                      'SessionID': str(validation_data["SessionID"]),
                      'SubSessionID': str(validation_data["SubSessionID"])}
        response = json.loads(session.get("https://trade.plus500.com/ClientRequest/GetChartDataImm", params=get_params).text)
        open_rates = self._bin_to_float(base64.b64decode(str(response["OpenRate"])))
        close_rates = self._bin_to_float(base64.b64decode(str(response["CloseRate"])))
        high_rates = self._bin_to_float(base64.b64decode(str(response["HighRate"])))
        low_rates = self._bin_to_float(base64.b64decode(str(response["LowRate"])))
        times = self._bin_to_datetime(base64.b64decode(str(response["DateTime"])))
        return np.stack((times, open_rates,close_rates,high_rates,low_rates), 1)

    def _bin_to_float(self, a):
        b=[]
        for c in range(0,len(a),4):
            d = 0
            for f in range(3,-1,-1):
                d = d * 256.0 + ord(a[c+f])
            f = math.floor(float(d) / float(1e8))
            d = d % float(1E8) * math.pow(10.0, -f)
            b.append(d)
        return b

    def _bin_to_datetime(self,a):
        b = []
        for c in range(0, len(a), 6):
            d = 0
            for f in range(3,-1,-1):
                d = d * 256 + ord(a[c+f])
            d *= 1E3
            d += 256 * ord(a[c+5]) + ord(a[c+4])
            b.append(d)
        return b

    def short(self, amount):
        return self._make_contract("Sell", amount)

    def buy(self, amount):
        return self._make_contract("Buy", amount)

    def _make_contract(self, type, amount):
        form_data = {'ModificationType': 'New',
                     'OrderID': '-1',
                     'InstrumentID': str(self._instrument_index["Id"]),
                     'InstrumentName' : "",
                     'Type': type,
                     'OrderEntryType': "Market",
                     'RequestedAmount': str(amount),
                     'MinRate': self._current_rate["Low"],
                     'MaxRate': self._current_rate["High"],
                     'ClientRate': self._current_rate[type+"Rate"],
                     'LimitRate' : -1,
                     'StopRate' : -1,
                     'OrderExpiration' : "1900-01-01 00:00:00.000",
                     'TrailingStopPips' : -1,
                     'IsGuaranteedStop' : "false",
                     'SessionID': str(self._validation_data["SessionID"]),
                     'SubSessionID': str(self._validation_data["SubSessionID"])}
        url1 = "https://trade.plus500.com/ClientRequest/ProcessOrder"
        concract_result = json.loads(self._session.post(url1, form_data).text)
        if concract_result["ResultCode"] != 0 or concract_result["ErrorDesc"] is not None:
            raise "Fatal error when making contract. ALERT!!!! " + str(concract_result)

        form_data = {'isHttpStreamEnabled': "false",
                      'sessID': str(self._validation_data["SessionID"]),
                      'subSessID': str(self._validation_data["SubSessionID"])}
        url2 = "https://trade.plus500.com/CometAsyncHandler.ashx"
        contract = None
        safety_counter = 0
        while contract is None:
            if safety_counter > 4:
                raise "Taking to long to get confirmation of order!!"
            contract_response = json.loads(self._session.post(url2, form_data).text)
            for item in contract_response:
                if item["Type"] == 12:
                    if item["NewOrder"]["Status"] != "Executed":
                        raise "Fatal error when making contract. ALERT!!!! " + item["NewOrder"]["Status"]
                if item["Type"] == 15:
                    contract = item["NewPosition"]
                    if float(contract["Amount"]) != amount:
                        raise "Amount missmatch between server and client!"
                if item["Type"] == 116:
                    self.ballance = item["AccountBalance"]["Balance"]
            safety_counter += 1
        return contract

    def cancel(self, contract):
        form_data = {'PositionID': str(contract["PID"]),
                     'Amount': str(contract["Amount"]),
                     'SessionID': str(self._validation_data["SessionID"]),
                     'SubSessionID': str(self._validation_data["SubSessionID"])}
        url1 = "https://trade.plus500.com/ClientRequest/ClosePosition"
        cancel_result = json.loads(self._session.post(url1, form_data).text)
        if cancel_result["ResultCode"] != 0 or cancel_result["ErrorDesc"] is not None:
            raise "Fatal error when canceling contract contract. ALERT!!!! " + str(concract_result)

ps = Plus500("Bitcoin",verbose=1)
h = ps.get_history(10)
while ps._current_rate == None:
    a = 7
#contract = ps.buy(0.25)
#ps.cancel(contract)
while True:
    d=3


