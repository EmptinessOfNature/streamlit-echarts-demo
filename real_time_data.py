import inspect
import os.path
import textwrap
import time
import json
import numpy as np
import pandas as pd
import streamlit as st

from demo_echarts import ST_DEMOS
from demo_pyecharts import ST_PY_DEMOS
import akshare as ak
from ibapi.client import Contract
from datetime import datetime
from ibapi.fufei6_exe import SimpleClient
from ibapi.celve import celve_5min
from download_data import download_data

def rt_read_data(client):

    contract = Contract()
    contract.symbol = "TSLA"
    contract.secType = "STK"
    contract.currency = "USD"
    # In the API side, NASDAQ is always defined as ISLAND in the exchange field
    contract.exchange = "ISLAND"


    # client.reqRealTimeBars(req_id, contract, 60, "MIDPOINT", True, [])



    for i in range(100):
        now = datetime.now().strftime("%Y%m%d %H:%M:%S")
        req_id='999'+now[6:8]+now[9:11]+now[12:14]
        data_path = 'data/' + str(req_id) + '.json'
        data_path_ready = 'data_ready_rt/' + str(req_id) + '.json'
        if not os.path.isfile(data_path):
            client.reqHistoricalData(
                req_id, contract, now, "1 D", "1 min", "TRADES", False, 1, False, []
            )
            time.sleep(5)
            try:
                ret = (
                        '[["dt", "open", "close", "high", "low", "vol", "cje", "zxj", "Code"],'
                        + open(data_path).readline()[:-1]
                        + "]"
                )
                with open(data_path_ready, "w") as f:
                    f.write(ret)
            except:
                print('no data'+data_path)
            time.sleep(5)
        else:
            print('数据已存在',req_id)
        print(i)

        # with open(data_path_ready) as f:
        #     raw_data = json.load(f)
        #     data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
        # data, fig = celve_5min(data, stockCode, stockDate, show_1d=1, is_huice=1)

    client.disconnect()