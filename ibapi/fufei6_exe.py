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
        print('Current timelpy: {}'.format(t))

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
        with open('data/historicalData.json','a') as f:
            # f.write(str(bar)+'\n')
            date = bar.date[0:4] + '-' +bar.date[4:6] +'-'+bar.date[6:8]+' '+bar.date[9:17]
            f.write('[\"'+str(date)+'\"' + ',' + str(bar.open) + ','+str(bar.close)
                    +',' + str(bar.high) +','+str(bar.low)+','+str(bar.volume)
                    +','+str(bar.volume) + ',' + str(bar.volume) + ','+ "\"" + "分时图" + "\""
                    +'],')
            # f.write('[\"' + str(date) + '\"' + ',' + str(bar.open) + ',' + str(bar.close - 10)
            #         + ',' + str(bar.high) + ',' + str(bar.low) + ',' + str(bar.volume)
            #         + ',' + str(bar.volume) + ',' + str(bar.volume) + ',' + "\"" + "标记点2" + "\""
            #         + '],')
        # print("HistoricalData. ReqId:", reqId, "BarData.", bar)

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
    def error(self, req_id, code, msg, advancedOrderRejectJson):
        print('Error {}: {}'.format(code, msg))


def main():
    # Create the client and connect to TWS
    client = SimpleClient('127.0.0.1', 7497, 0)
    client.reqCurrentTime()
    # Sleep while the request is processed
    time.sleep(0.5)

    contract = Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.currency = "USD"
    contract.exchange = "IDEALPRO"
    client.reqContractDetails(1, contract)
    # print("self.conn",client.conn)
    # print("self.isConnected()",client.isConnected())
    time.sleep(2)

    # Define the limit order
    order = Order()
    # order.action = 'SELL'
    order.action = 'BUY'
    order.totalQuantity = 230813
    order.orderType = 'MKT'
    # Obtain a valid ID for the order
    # client = SimpleClient('127.0.0.1', 7497, 0)
    client.reqIds(1)
    time.sleep(0.5)
    order_id = max(client.order_id,1)
    # Place the order
    print("order_id",order_id)
    if order_id:
        # client = SimpleClient('127.0.0.1', 7497, 0)
        # print("self.conn",client.conn)
        # print("self.isConnected()",client.isConnected())
        time.sleep(0.1)
        client.placeOrder(order_id, contract, order)
        time.sleep(1)
        print("下单成功")
    else:
        print('Order ID not received. Ending application.')
        # sys.exit()

    # Obtain information about open positions
    # client = SimpleClient('127.0.0.1', 7497, 0)
    # 读取账户当前仓位
    client.reqPositions()
    time.sleep(2)

    # Obtain information about account
    # client = SimpleClient('127.0.0.1', 7497, 0)
    # 读取用户当前账户类型和可用余额
    client.reqAccountSummary(0, 'All', 'AccountType,AvailableFunds')
    time.sleep(2)

    # Request the current time

    # Request ten ticks containing midpoint data

    print("获取bidask的数据")
    client.reqTickByTickData(1, contract, 'BidAsk', 1, True)
    client.reqTickByTickData(3, contract, 'MidPoint', 1, False)
    # time.sleep(5)
    # print("获取last的数据")
    # client.reqTickByTickData(2, contract, 'Last', 1, False)
    # time.sleep(5)
    # print("获取alllast的数据")
    # client.reqTickByTickData(3, contract, 'AllLast', 1, True)
    # time.sleep(10)
    # print("获取midpoint的数据")
    # client.reqTickByTickData(0, contract, 'MidPoint', 1, True)
    # time.sleep(5)

    # Request market data
    # client.reqMktData(4, contract, '', False, False, [])

    # Request current bars
    # client.reqRealTimeBars(5, contract, 10, 'MIDPOINT', True, [])

    # Request historical bars
    # now = datetime.now().strftime("%Y%m%d, %H:%M:%S")
    # client.reqHistoricalData(6, contract, now, '2 w', '1 day',
    #     'MIDPOINT', False, 1, False, [])
    # 请求历史直方图数据
    # client.reqHistogramData(7,contract,1,"3 days")

    # 请求历史tick数据
    # client.reqHistoricalTicks(8,contract,"20211230 21:39:33", "", 10, "TRADES", 1, True, [])
    # Request fundamental data
    con = Contract()
    con.symbol = 'IBM'
    con.secType = 'STK'
    con.exchange = 'SMART'
    con.currency = 'USD'
    client.reqFundamentalData(9, con, 'ReportSnapshot', [])

    # Sleep while the requests are processed
    time.sleep(5)

    # Sleep while the request is processed
    client.disconnect()

def read_data_fq():


    contract = Contract()
    contract.symbol = "TSLA"
    contract.secType = "STK"
    contract.currency = "USD"
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = "ISLAND"

    client = SimpleClient('127.0.0.1', 7497, 1)

    # client.reqCurrentTime()
    now = datetime.now().strftime("%Y%m%d %H:%M:%S")
    client.reqHistoricalData(10, contract, now, '1 w', '1 min', 'MIDPOINT', False, 1, False, [])
    time.sleep(4)
    # client.reqHistogramData(7, contract, 1, "3 days")
    print('开始接收数据')
    # client.disconnect()

if __name__ == '__main__':
    # main()
    read_data_fq()
