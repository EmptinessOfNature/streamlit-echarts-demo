from datetime import datetime
from threading import Thread
import time
import sys
from ibapi.client import EClient, Contract
from ibapi.order import Order
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper


class SimpleClient(EWrapper, EClient):
    ''' Serves as the client and the wrapper '''

    def __init__(self, addr, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        # 订单号
        self.order_id = 0

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
    def contractDetails(self, reqId, details):
        print('Long name: {}'.format(details.longName))
        print('Category: {}'.format(details.category))
        print('Subcategory: {}'.format(details.subcategory))
        print('Contract ID: {}\n'.format(details.contract.conId))

    @iswrapper
    def contractDetailsEnd(self, reqId):
        print('The End')

    @iswrapper
    def nextValidId(self, order_id):
        ''' Provides the next order ID '''
        self.order_id = order_id
        print('Order ID: {}'.format(order_id))

    @iswrapper
    def openOrder(self, order_id, contract, order, state):
        ''' Called in response to the submitted order '''
        print('Order status: '.format(state.status))
        print('Commission charged: '.format(state.commission))

    @iswrapper
    def orderStatus(self, order_id, status, filled, remaining, avgFillPrice, \
                    permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        ''' Check the status of the subnitted order '''
        print('Number of filled positions: {}'.format(filled))
        print('Average fill price: {}'.format(avgFillPrice))

    @iswrapper
    def position(self, account, contract, pos, avgCost):
        ''' Read information about the account's open positions '''
        print('Position in {}: {}'.format(contract.symbol, pos))

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        ''' Read information about the account '''
        print('Account {}: {} = {}'.format(account, tag, value))

    @iswrapper
    def tickByTickMidPoint(self, reqId: int, time: int, midPoint: float):
        super().tickByTickMidPoint(reqId, time, midPoint)
        print("Midpoint. ReqId:", reqId, "Time:", datetime.fromtimestamp(time), "MidPoint:", midPoint)

    @iswrapper
    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float, bidSize, askSize,
                         tickAttribBidAsk):
        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk)
        print("BidAsk. ReqId:", reqId, "Time:", datetime.fromtimestamp(time),
              "BidPrice:", bidPrice, "AskPrice:", askPrice, "BidSize:", bidSize, "AskSize:", askSize, "BidPastLow:",
              tickAttribBidAsk.bidPastLow, "AskPastHigh:", tickAttribBidAsk.askPastHigh)

    @iswrapper
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size, tickAtrribLast, exchange: str, specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAtrribLast,
                                  exchange, specialConditions)
        if tickType == 1:
            print("Last.", end='')
        else:
            print("AllLast.", end='')
            print(" ReqId:", reqId,
                  "Time:", datetime.fromtimestamp(time),
                  "Price:", price, "Size:", size, "Exch:", exchange,
                  "Spec Cond:", specialConditions, "PastLimit:", tickAtrribLast.pastLimit,
                  "Unreported:", tickAtrribLast.unreported)

    @iswrapper
    def tickPrice(self, reqId, tickType, price: float, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
              "Price:", price, "CanAutoExecute:", attrib.canAutoExecute,
              "PastLimit:", attrib.pastLimit, end=' ')

    @iswrapper
    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)
        print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size: ", size)

    @iswrapper
    def tickGeneric(self, reqId, tickType, value: float):
        super().tickGeneric(reqId, tickType, value)
        print("TickGeneric. TickerId:", reqId, "TickType:", tickType, "Value:", value)

    @iswrapper
    def realtimeBar(self, reqId, time, open, high, low, close, volume, WAP, count):
        ''' Called in response to reqRealTimeBars '''

        print('realtimeBar:{},time:{} - Opening : {},high :{},low :{},close :{},volume :{},WAP :{},count :{}'.format(
            reqId, datetime.fromtimestamp(time), open, high, low, close, volume, WAP, count))

    @iswrapper
    def historicalData(self, reqId: int, bar):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    @iswrapper
    def historicalDataUpdate(self, reqId: int, bar):
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)

    @iswrapper
    def histogramData(self, reqId: int, items):
        print("HistogramData. ReqId:", reqId, "HistogramDataList:", "[%s]" % "; ".join(map(str, items)))

    @iswrapper
    def historicalTicks(self, reqId: int, ticks, done: bool):
        for tick in ticks:
            print("HistoricalTick. ReqId:", reqId, tick)

    @iswrapper
    def historicalTicksBidAsk(self, reqId: int, ticks, done: bool):
        for tick in ticks:
            print("HistoricalTickBidAsk. ReqId:", reqId, tick)

    @iswrapper
    def historicalTicksLast(self, reqId: int, ticks, done: bool):
        for tick in ticks:
            print("HistoricalTickLast. ReqId:", reqId, tick)

    @iswrapper
    def fundamentalData(self, reqId, data):
        ''' Called in response to reqFundamentalData '''

        print('Fundamental data: ' + data)

    @iswrapper
    def error(self, req_id, code, msg):
        print('Error {}: {}'.format(code, msg))


### 2 步 打开tws
### 3 步 实例化 SimpleClient
client = SimpleClient('127.0.0.1', 7497, 0)
### 输出服务器当前时间
client.reqCurrentTime()
print('111')

time.sleep(0.5)

### 定义EURUSD Contract()类 用来请求 stream tick 数据流
contract = Contract()
contract.symbol = "EUR"
contract.secType = "CASH"
contract.currency = "USD"
contract.exchange = "IDEALPRO"

### 请求数据流 client.reqMktData
# client.reqMktData(5, contract, '', False, False,[])
client.reqPositions()
