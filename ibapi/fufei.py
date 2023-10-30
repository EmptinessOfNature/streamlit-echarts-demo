from datetime import datetime
from threading import Thread
import time

from ibapi.client import EClient,Contract
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

class SimpleClient(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EClient. __init__(self, self)

        # Connect to TWS
        self.connect(addr, port, client_id)

        # Launch the client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def currentTime(self, cur_time):
        t = datetime.fromtimestamp(cur_time)
        print('Current time: {}'.format(t))

    @iswrapper
    def error(self, req_id, code, msg, advancedOrderRejectJson):
        print('Error {}: {}'.format(code, msg))

def main():

    # Create the client and connect to TWS
    import logging
    logging.getLogger().setLevel(logging.INFO)
    client = SimpleClient('127.0.0.1', 7497, 0)

    # Request the current time
    client.reqCurrentTime()
    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.currency = "GBP"
    contract.exchange = "IDEALPRO"


    # Request ten ticks containing midpoint data
    client.reqTickByTickData(0, contract, 'MidPoint', 10, True)

    # Request market data
    client.reqMktData(1, contract, '', False, False, [])

    # Request current bars
    # client.reqRealTimeBars(2, contract, 5, 'MIDPOINT', True, [])

    # Request historical bars
    now = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    # now = client.reqCurrentTime()
    print('now',now)
    client.reqHistoricalData(3, contract, now, '2 w', '1 day',
                             'MIDPOINT', False, 1, False, [])

    # Request fundamental data
    # client.reqFundamentalData(4, contract, 'ReportSnapshot', [])

    # Sleep while the request is processed
    time.sleep(0.5)

    # Disconnect from TWS
    client.disconnect()

if __name__ == '__main__':
    main()
