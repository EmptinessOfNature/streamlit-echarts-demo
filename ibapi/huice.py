from celve import signal_1
import pandas as pd
import json

import akshare as ak
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from MyTT import *
import ibapi.indicator as i


def huice_csv2json():
    data_name = 'QQQ'
    data = pd.read_csv("../data_hist/"+data_name+".csv")
    print(1)


    ret = '[["dt", "open", "close", "high", "low", "vol", "cje", "zxj", "Code"],'

    for i in range(1,len(data)):
        l = (
            '["'
            + str(data.iloc[i]["date"])
            + '",'
            + str(float(data.iloc[i]["开盘价"]))
            + ","
            + str(float(data.iloc[i]["收盘价"]))
            + ","
            + str(float(data.iloc[i]["最高价"]))
            + ","
            + str(float(data.iloc[i]["最低价"]))
            + ","
            + str(int(data.iloc[i]["成交量(股)"]))
            + ","
            + str(int(data.iloc[i]["成交量(股)"]))
            + ","
            + str(int(data.iloc[i]["成交量(股)"]))
            + ',"分时图"'
            + "],"
        )
        ret += l
    ret=ret[:-1]+']'
    data_path_hist_ready = '../data_hist/'+data_name+'.json'
    with open(data_path_hist_ready, "w") as f:
        f.write(ret)

    print(1)

def zhiying(data,zhiying_perc=0.005,zhisun_perc=0.005):
    # 对于做多点，记录买入后的高点，当前价格低于最高点的止盈比例，则卖掉。
    long_index = data[data['buy_signal']>=1].index
    short_index = data[data['sell_signal'] >= 1].index
    long_end_index = []
    short_end_index = []
    for i in long_index:
        high = data.iloc[i]['close']
        for j in range(400):
            if int(data.iloc[i+j]['dt'][11:13])==4 and int(data.iloc[i+j]['dt'][14:16])==30:
                # 如果到最后10分钟，则直接卖掉
                long_end_index.append(i+j)
                continue
            elif data.iloc[i+j]['sell_signal']>= 1:
                # 出现卖出信号则卖
                long_end_index.append(i + j)
                continue
            else:
                # 计算止盈
                cur_price = data.iloc[i+j]['close']
                if cur_price>high:
                    high = cur_price
                if high/cur_price - 1>=zhiying_perc:
                    long_end_index.append(i + j)
                    continue

def celve_huice(data, stockCode,stockDate,is1d=0):
    # 数据只保留stockDate的17:00到次日的09:00
    if is1d:
        stockDate_plus1 = stockDate[:3] + str(int(stockDate[3:5]) + 1)
        data_1d = data[
            (
                    (data["dt"].str.contains(stockDate))
                    & (
                            (data["dt"].str[11:13] + data["dt"].str[14:16]).astype(int)
                            >= 2230
                    )
            )
            | (
                    (data["dt"].str.contains(stockDate_plus1))
                    & (
                            (data["dt"].str[11:13] + data["dt"].str[14:16]).astype(int)
                            <= 500
                    )
            )
            ]
        data_1d = data_1d.reset_index(drop=True)
    else:
        data_1d = data

    dt_all = pd.date_range(
        start=data_1d["dt"].iloc[0], end=data_1d["dt"].iloc[-1], freq="1min"
    )
    dt_all = [d.strftime("%Y-%m-%d %H:%M:%S") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(data_1d["dt"]))

    # 获取5min\30min数据

    data_5min = data.groupby(data.index // 5).agg({'dt': 'first',
                                             'open': 'first',
                                             'close': 'last',
                                             'high': 'max',
                                             'low': 'min',
                                             'vol': 'sum',
                                             'cje': 'sum',
                                             'zxj': 'sum',
                                             'Code': 'first'})
    data_30min = data.groupby(data.index // 30).agg({'dt': 'first',
                                             'open': 'first',
                                             'close': 'last',
                                             'high': 'max',
                                             'low': 'min',
                                             'vol': 'sum',
                                             'cje': 'sum',
                                             'zxj': 'sum',
                                             'Code': 'first'})

    # 盆形低判断
    ne = 45
    m1e = 15
    m2e = 15
    data_5min["RSVM"] = (
        (data_5min["close"] - LLV(data_5min["low"], ne))
        / (HHV(data_5min["high"], ne) - LLV(data_5min["low"], ne))
        * 100
    )
    data_5min["KW"] = SMA(data_5min["RSVM"], m1e)
    data_5min["DW"] = SMA(data_5min["KW"], m2e)
    data_5min["JW_5"] = 3 * data_5min["KW"] - 2 * data_5min["DW"]
    # 30min
    data_30min["RSVM"] = (
        (data_30min["close"] - LLV(data_30min["low"], ne))
        / (HHV(data_30min["high"], ne) - LLV(data_30min["low"], ne))
        * 100
    )
    data_30min["KW"] = SMA(data_30min["RSVM"], m1e)
    data_30min["DW"] = SMA(data_30min["KW"], m2e)
    data_30min["JW_30"] = 3 * data_30min["KW"] - 2 * data_30min["DW"]

    data_1d = pd.merge(data_1d, data_5min[['dt', 'JW_5']], how='left', on='dt')
    data_1d = pd.merge(data_1d, data_30min[['dt', 'JW_30']], how='left', on='dt')
    for i in range(len(data_1d)):
        if pd.isna(data_1d.at[i, 'JW_5']):
            try:
                tmp = data_1d['JW_5'].iloc[max(0, i - 5):i].dropna().iloc[-1]
            except:
                tmp = np.nan
            data_1d.at[i, 'JW_5'] = tmp
        if pd.isna(data_1d.at[i, 'JW_30']):
            try:
                tmp_30 = data_1d['JW_30'].iloc[max(0, i - 31):i].dropna().iloc[-1]
            except:
                tmp_30 = np.nan
            data_1d.at[i, 'JW_30'] = tmp_30

    data_1d["DI_5min"] = 1 * (data_1d["JW_5"] < 0)
    data_1d["DING_5min"] = 1 * (data_1d["JW_5"] > 100)
    data_1d["DI_30min"] = 1 * (data_1d["JW_30"] < 0)
    data_1d["DING_30min"] = 1 * (data_1d["JW_30"] > 100)
    print(1)

    # signal的买卖点判断
    data_1d["volume"] = data_1d["vol"]
    (
        icon_1,
        icon_2,
        icon_11,
        icon_12,
        icon_13,
        icon_34,
        icon_35,
        icon_38,
        icon_39,
        icon_41,
    ) = signal_1(data_1d)
    data_1d["icon_1"] = icon_1
    data_1d["icon_2"] = icon_2
    data_1d["icon_11"] = icon_11
    data_1d["icon_12"] = icon_12
    data_1d["icon_13"] = icon_13.astype('int')
    data_1d["icon_34"] = icon_34
    data_1d["icon_35"] = icon_35
    data_1d["icon_38"] = icon_38
    data_1d["icon_39"] = icon_39
    data_1d["icon_41"] = icon_41.astype('int')

    # data_1d['buy_signal'] = (data_1d['DI_5min'] * data_1d['DI_30min']) * (1*data_1d['icon_1'] + 2*data_1d['icon_38']+ 3*data_1d['icon_34']+ 4*data_1d['icon_13']+ 5*data_1d['icon_11'])
    # data_1d['sell_signal'] = (data_1d['DING_5min'] * data_1d['DING_30min']) * (1*data_1d['icon_2'] + 2*data_1d['icon_39']+ 3*data_1d['icon_35']+ 4*data_1d['icon_12']+ 5*data_1d['icon_41'])

    data_1d['buy_signal'] = (1*data_1d['icon_1'] + 2*data_1d['icon_38']+ 3*data_1d['icon_34']+ 4*data_1d['icon_13']+ 5*data_1d['icon_11'])
    data_1d['sell_signal'] = (1*data_1d['icon_2'] + 2*data_1d['icon_39']+ 3*data_1d['icon_35']+ 4*data_1d['icon_12']+ 5*data_1d['icon_41'])

    print(1)
    file_path = '../data_calc/'+stockCode+stockDate+'.csv'

    data_1d.to_csv(file_path)
    # fig = plot_cand_volume(data_1d, dt_breaks)

    return data_1d


# with open(data_path_hist_ready) as f:
#     raw_data = json.load(f)
#     data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
#     data = data[data["dt"].str[5:7].astype(int)== 1]
#     print(len(data))
#
# data = celve_huice(data,'QQQ','huice',is1d=0)
# zhiying(data)
huice_csv2json()