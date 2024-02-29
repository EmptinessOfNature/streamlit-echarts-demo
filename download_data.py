import os.path
import time
from ibapi.client import Contract
from datetime import datetime
from ibapi.fufei6_exe import SimpleClient


def download_data(stock_dict,stockCode,client):
    contract = Contract()
    # contract.symbol = "TSLA"
    contract.symbol = stockCode
    contract.secType = "STK"
    contract.currency = "USD"
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = "ISLAND"
    now = datetime.now().strftime("%Y%m%d %H:%M:%S")
    req_id = int(stock_dict[stockCode] + now[2:8])
    print('req_id', req_id)
    data_path = 'data/' + str(req_id) + '.json'
    data_path_ready = 'data_ready/' + str(req_id) + '.json'
    if not os.path.isfile(data_path):
        print("数据不存在，读取得到")
        client.reqHistoricalData(
            req_id, contract, now, "1 w", "1 min", "TRADES", False, 1, False, []
        )
        # client.reqHistoricalData(req_id, contract, now, '1 w', '1 min', 'ADJUSTED_LAST', False, 1, False, [])
        time.sleep(15)
        # ret = (
        #         '[["dt", "open", "close", "high", "low", "vol", "cje", "zxj", "Code"],'
        #         + open(data_path).readline()[:-1]
        #         + "]"
        # )
        # with open(data_path_ready, "w") as f:
        #     f.write(ret)
    else:
        print('数据已存在，不需要下载')
        time.sleep(1)

