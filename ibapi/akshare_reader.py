import akshare as ak
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from MyTT import *


def get_stock_price(share, start_date="20230815", end_date="20230816"):
    # 获取个股行情数据
    # stock_zh_a_hist_df = ak.stock_zh_a_hist_min_em(symbol=share, start_date=start_date,
    #                                                       end_date=end_date, period='1', adjust='')
    # stock_zh_a_hist_df = ak.stock_zh_a_minute(symbol=share, period='1', adjust='qfq')
    stock_zh_a_hist_df = ak.stock_us_hist_min_em(symbol="105.QQQ")
    return stock_zh_a_hist_df


def get_trading_date():
    # 获取市场的交易时间
    trade_date = ak.tool_trade_date_hist_sina()["trade_date"]
    trade_date = [d.strftime("%Y-%m-%d %H:%M:%S") for d in trade_date]
    return trade_date

def data2json(data):
    data_list = data.values.tolist()
    # data_list.insert(0, data.columns.to_list())
    data['Code'] ='105.QQQ'
    data_list.insert(0, ['dt','open','close','high','low','vol','cje','zxj','Code'])
    f = open('./105qqq.json', 'w')
    f.write(str(data_list))
    f.close()


def plot_cand_volume(data, dt_breaks):
    # Create subplots and mention plot grid size
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(""),
        row_width=[1, 1, 1, 1],
    )

    # 绘制k数据
    # fig.add_trace(go.Candlestick(x=data["date"], open=data["open"], high=data["high"],
    #                              low=data["low"], close=data["close"], name=""),
    #               row=1, col=1
    #               )

    # 走势图
    fig.add_trace(go.Scatter(x=data["date"], y=data["close"]), row=1, col=1)

    # 绘制成交量数据
    fig.add_trace(
        go.Bar(x=data["date"], y=data["volume"], showlegend=False), row=2, col=1
    )

    # 绘制策略点
    fig.add_trace(go.Bar(x=data["date"], y=data["XG"], showlegend=False), row=3, col=1)

    fig.add_trace(
        go.Scatter(x=data["date"], y=data["JW"], showlegend=False), row=4, col=1
    )

    # fig.update_xaxes(
    #     title_text='date',
    #     rangeslider_visible=True,  # 下方滑动条缩放
    #     rangeselector=dict(
    #         # 增加固定范围选择
    #         buttons=list([
    #             dict(count=1, label='1M', step='month', stepmode='backward'),
    #             dict(count=6, label='6M', step='month', stepmode='backward'),
    #             dict(count=1, label='1Y', step='year', stepmode='backward'),
    #             dict(count=1, label='YTD', step='year', stepmode='todate'),
    #             dict(step='all')])))

    # # Do not show OHLC's rangeslider plot
    # fig.update(layout_xaxis_rangeslider_visible=False)
    # # 去除休市的日期，保持连续
    # fig.update_xaxes(tickformat = "%Y-%m-%d %H:%M:%S" ,rangebreaks=[dict(values=dt_breaks)])

    # fig.update_xaxes(tickformat = "%Y-%m-%d %H:%M:%S" ,rangebreaks=[dict(values=dt_breaks)])
    # fig.update_xaxes(tickformat = "%Y-%m-%d %H:%M:%S",rangebreaks=[dict(values=["2023-08-17 13:50:00"])])
    # A股break时间
    # fig.update_xaxes(tickformat="%Y-%m-%d %H:%M:%S", rangebreaks=[dict(bounds=[11.5, 13], pattern="hour"),dict(bounds=[15, 9.5], pattern="hour"),dict(bounds=[6,1], pattern="day of week")])
    fig.update_xaxes(
        tickformat="%Y-%m-%d %H:%M:%S",
        rangebreaks=[
            dict(bounds=[4, 21.5], pattern="hour"),
            dict(bounds=[6, 1], pattern="day of week"),
        ],
    )
    hovertext = []  # 添加悬停信息

    for i in range(len(data["close"])):  # <br>表示
        hovertext.append(
            "时间: " + str(data["date"][i]) + "<br>价格: " + str(data["close"][i])
        )

    fig.update_layout(hovermode="x unified")

    return fig


def SMA(close, n):
    weights = np.array(range(1, n + 1))
    sum_weights = np.sum(weights)
    res = close.rolling(window=n).apply(
        lambda x: np.sum(weights * x) / sum_weights, raw=False
    )
    return res


def LLV(x, n):
    return x.rolling(window=n).min()


def HHV(x, n):
    return x.rolling(window=n).max()

def drawIcon(data_raw, index, xishu, tubiao, color):
    # index = "XG_IN"
    # xishu = 1.02
    # tubiao = '⛛'
    # color = "red"
    data_new = data_raw[data_raw[index] == True]
    fig.add_trace(go.Scatter(
        x=data_new["date"],
        y=data_new[index]*data_new["close"]*xishu, mode='text', text=tubiao, marker={"color":color}), row=1, col=1)

def celve1():
    save_flag = 1
    if save_flag:
        data = get_stock_price(
            share="sh000001",
            start_date="2023-08-20 00:00:00",
            end_date="2023-08-25 20:59:00",
        )
        data.to_csv("./sh000001_minute.csv")
        print("数据保存完成")
    else:
        print("读取本地csv")
        data = pd.read_csv("./sh000001_minute.csv")
    data = data.rename(
        columns={
            "时间": "date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
        }
    )
    # columns = {'day': 'date'})
    data["open"] = data["open"].astype("float")
    data["close"] = data["close"].astype("float")
    data["high"] = data["high"].astype("float")
    data["low"] = data["low"].astype("float")
    data["volume"] = data["volume"].astype("float")
    # 取固定dt的数据
    data = data[data["date"] >= "2023-08-11 08:00:00"]
    dt_all = pd.date_range(
        start=data["date"].iloc[0], end=data["date"].iloc[-1], freq="1min"
    )
    dt_all = [d.strftime("%Y-%m-%d %H:%M:%S") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(data["date"]))
    # 绘制 复杂k线图

    # 5、30min买入、卖出点判断
    ne = 45
    m1e = 15
    m2e = 15
    data["RSVM"] = (
        (data["close"] - LLV(data["low"], ne))
        / (HHV(data["high"], ne) - LLV(data["low"], ne))
        * 100
    )
    data["KW"] = SMA(data["RSVM"], m1e)
    data["DW"] = SMA(data["KW"], m2e)
    data["JW"] = 3 * data["KW"] - 2 * data["DW"]
    data["XG_IN"] = 1 * (data["JW"] < 0)
    data["XG_OUT"] = -1 * (data["JW"] > 100)
    data["XG"] = data["XG_IN"] + data["XG_OUT"]
    print('5,30分钟盆形底部策略')

    # 分时图nm
    data["dt"] = pd.to_datetime(data["date"])
    data["year"] = data["dt"].apply(lambda x: x.year)
    data["month"] = data["dt"].apply(lambda x: x.month)
    data["day"] = data["dt"].apply(lambda x: x.day)
    data["hour"] = data["dt"].apply(lambda x: x.hour)
    data["minute"] = data["dt"].apply(lambda x: x.minute)
    data["second"] = data["dt"].apply(lambda x: x.second)
    data["yyyymmdd"] = data["dt"].apply(
        lambda x: str(x.year)
        + str("" if x.month >= 10 else "0")
        + str(x.month)
        + str("" if x.day >= 10 else "0")
        + str(x.day)
    )
    data["yyyymmdd_lst1d"] = data.set_index("dt").shift(-1, freq="D").index.day
    data["hhmmss"] = data["dt"].apply(
        lambda x: str("" if x.hour >= 10 else "0")
        + str(x.hour)
        + str("" if x.minute >= 10 else "0")
        + str(x.minute)
        + str("" if x.second >= 10 else "0")
        + str(x.second)
    )

    # nm策略
    """
    data['X_1'] = data['close']
    ZSTJJ = data.groupby(data.yyyymmdd).close.mean()
    data['X_2'] = pd.merge(data,ZSTJJ,on='yyyymmdd',how='left').iloc[:,-1]

    # X_3:=SUM(CLOSE*VOL,0)/SUM(VOL,0);
    data['X_3'] = (data.close*data.volume).sum()/data.volume.sum()
    data['X_14'] = REF(data.close,1)
    #X_15:=SMA(MAX(CLOSE-X_14,0),14,1)/SMA(ABS(CLOSE-X_14),14,1)*100;
    data['X_15'] = SMA(MAX(data.close-data.X_14,0),14)/SMA(ABS(data.close-data.X_14),14)*100
    # X_16 := CROSS(80, X_15);
    data['X_16'] = CROSS(80,data.X_15)[1:]
    # X_17 := FILTER(X_16, 60) AND CLOSE / X_3 > 1.005;
    data['X_17'] = FILTER(data.X_16,60) & (data.close/data.X_3 >1.005)
    # DRAWICON(X_17, CLOSE * 1.003, 41);

    # shoupan = data[data['hhmmss']=='040000'].reset_index()
    # # data['lstsp'] = data['yyyymmdd'].apply(lambda x :  shoupan.iloc[shoupan[shoupan['yyyymmdd']==x].index-1].close)
    # data['lstsp'] = 0.0
    # for i in range(len(data)):
    #     if len(shoupan.iloc[shoupan[shoupan['yyyymmdd']==data['yyyymmdd'][i]].index-1].close)>=1:
    #         t = float(shoupan.iloc[shoupan[shoupan['yyyymmdd']==data['yyyymmdd'][i]].index-1].close)
    #         data['lstsp'][i] = t
    """

    # nm策略重写
    # 改成纽约时间
    import pytz
    data.dt_sh = datetime.datetime.now()
    data.dt_sh = data.dt.apply(lambda x: x.to_pydatetime().astimezone(pytz.timezone('America/New_York')))
    N = 5
    M = 15
    data['X_1'] = data['close']
    ZSTJJ = data.groupby(data.yyyymmdd).close.mean()
    data['X_2'] = pd.merge(data,ZSTJJ,on='yyyymmdd',how='left').iloc[:,-1]
    data['X_3'] = (data.close * data.volume).sum() / data.volume.sum()
    data['X_14'] = REF(data.close, 1)
    data['X_15'] = SMA(MAX(data.close - data.X_14, 0), 14) / SMA(ABS(data.close - data.X_14), 14) * 100
    data['X_16'] = CROSS(80, np.array(data.X_15))
    data['X_17'] = FILTER(data.X_16, 60) & (data.close / data.X_3 > 1.005)
    data['drawicon_x17'] = data['X_17']
    data['X_18'] = CROSS(data.X_15,20)[1:]
    data['X_19'] = FILTER(data.X_18,60) & ((data.close/data.X_3)<0.995)
    data['drawicon_x19'] = data['X_19']
    data['X_20'] = (data.close>REF(data.close,1)) & ((data.close/data.X_2)>(1+N/1000))
    data['X_21'] = (data.close<REF(data.close,1)) & ((data.close/data.X_2)<(1-N/1000))
    data['X_22'] = CROSS(SUM(data.X_20,0),0.5)
    data['X_23'] = CROSS(SUM(data.X_21, 0), 0.5)
    # X_24 := SUM(X_22, 0) * CROSS(COUNT(CLOSE < REF(CLOSE, 1), BARSLAST(X_22)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_22)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close<REF(data.close,1),data.tmp2[i])[i]
        data.loc[i,'tmp3'] = tmp
    data['X_24'] = SUM(data.X_22,0) * CROSS(data.tmp3,0.5)[1:]
    # X_25:=SUM(X_23,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_23)),0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_23)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close > REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_25'] = SUM(data.X_23, 0) * CROSS(data.tmp3, 0.5)[1:]
    # X1: CONST(SUM(IF(X_24, REF(CLOSE, 1), DRAWNULL), 0)), DOTLINE, COLORYELLOW;
    data['X1'] = CONST(SUM(IF(data.X_24,REF(data.close,1),np.nan),0))
    # Z1: CONST(SUM(IF(X_25, REF(CLOSE, 1), DRAWNULL), 0)), DOTLINE, COLORGREEN;
    data['Z1'] = CONST(SUM(IF(data.X_25, REF(data.close,1), np.nan), 0))
    # X_26 := CROSS(SUM(X_20 AND CLOSE > X1 * (1 + 1 / 100), 0), 0.5);
    data['X_26'] = CROSS(SUM(data.X_20 & (data.close > (data.X1 * (1+1/100))),0),0.5)
    data['X_27'] = CROSS(SUM(data.X_21 & (data.close < (data.Z1 * (1 - 1 / 100))), 0), 0.5)
    # X_28 := SUM(X_26, 0) * CROSS(COUNT(CLOSE < REF(CLOSE, 1), BARSLAST(X_26)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_26)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close < REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_28'] = SUM(data.X_27, 0) * CROSS(data.tmp3, 0.5)[1:]
    # X_29 := SUM(X_27, 0) * CROSS(COUNT(CLOSE > REF(CLOSE, 1), BARSLAST(X_27)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_27)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close > REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_29'] = SUM(data.X_27, 0) * CROSS(data.tmp3, 0.5)[1:]
    # X2: CONST(SUM(IF(X_28, REF(CLOSE, 1), DRAWNULL), 0)), COLORWHITE;
    # Z2: CONST(SUM(IF(X_29, REF(CLOSE, 1), DRAWNULL), 0)), COLORGREEN;
    data['X2'] = CONST(SUM(IF(data.X_28, REF(data.close, 1), np.nan), 0))
    data['Z2'] = CONST(SUM(IF(data.X_29, REF(data.close, 1), np.nan), 0))
    # DRAWICON(X_25, REF(CLOSE * 0.9999, 1), 1);
    # DRAWICON(X_29, REF(CLOSE * 0.9999, 1), 34);
    # DRAWICON(X_24, REF(CLOSE * 1.0015, 1), 2);
    # DRAWICON(X_28, REF(CLOSE * 1.0015, 1), 35);

    # X_30 := CLOSE > REF(CLOSE, 1) AND CLOSE / X_2 > 1 + M / 1000;
    # X_31 := CLOSE < REF(CLOSE, 1) AND CLOSE / X_2 < 1 - M / 1000;
    data['X_30'] = (data.close > REF(data.close,1)) & ((data.close/data.X_2)>(1+M/1000))
    data['X_31'] = (data.close < REF(data.close, 1)) & ((data.close / data.X_2) < (1 - M / 1000))

    # X_32 := CROSS(SUM(X_30, 0), 0.5);
    # X_33 := CROSS(SUM(X_31, 0), 0.5);
    data['X_32'] = CROSS(SUM(data.X_30,0),0.5)
    data['X_33'] = CROSS(SUM(data.X_31, 0), 0.5)
    # X_34 := SUM(X_32, 0) * CROSS(COUNT(CLOSE < REF(CLOSE, 1), BARSLAST(X_32)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_32)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close < REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_34'] = SUM(data.X_32, 0) * CROSS(data.tmp3, 0.5)[1:]
    # X_35 := SUM(X_33, 0) * CROSS(COUNT(CLOSE > REF(CLOSE, 1), BARSLAST(X_33)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_33)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close > REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_35'] = SUM(data.X_33, 0) * CROSS(data.tmp3, 0.5)[1:]
    # X_36 := CONST(SUM(IF(X_34, REF(CLOSE, 1), DRAWNULL), 0));
    # X_37 := CONST(SUM(IF(X_35, REF(CLOSE, 1), DRAWNULL), 0));
    data['X_36'] = CONST(SUM(IF(data.X_34, REF(data.close, 1), np.nan), 0))
    data['X_37'] = CONST(SUM(IF(data.X_35, REF(data.close, 1), np.nan), 0))
    # X_38 := CROSS(SUM(X_30 AND CLOSE > X_36 * 1.02, 0), 0.5);
    # X_39 := CROSS(SUM(X_31 AND CLOSE < X_37 * 0.98, 0), 0.5);
    data['X_38'] = CROSS(SUM(data.X_30 & (data.close > (data.X_36 * 1.02)), 0), 0.5)
    data['X_39'] = CROSS(SUM(data.X_31 & (data.close < (data.X_37 * 0.98)), 0), 0.5)
    # X_40 := SUM(X_38, 0) * CROSS(COUNT(CLOSE < REF(CLOSE, 1), BARSLAST(X_38)), 0.5);
    # X_41 := SUM(X_39, 0) * CROSS(COUNT(CLOSE > REF(CLOSE, 1), BARSLAST(X_39)), 0.5);
    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_38)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close < REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_40'] = SUM(data.X_38, 0) * CROSS(data.tmp3, 0.5)[1:]

    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_39)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close > REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_41'] = SUM(data.X_39, 0) * CROSS(data.tmp3, 0.5)[1:]

    # X_42 := CONST(SUM(IF(X_40, REF(CLOSE, 1), DRAWNULL), 0));
    # X_43 := CONST(SUM(IF(X_41, REF(CLOSE, 1), DRAWNULL), 0));
    data['X_42'] = CONST(SUM(IF(data.X_40, REF(data.close, 1), np.nan), 0))
    data['X_43'] = CONST(SUM(IF(data.X_41, REF(data.close, 1), np.nan), 0))

    # DRAWICON(X_40, CLOSE * 1.002, 12);
    # DRAWICON(X_41, CLOSE * 0.998, 11);

    # X_44 := CLOSE > REF(CLOSE, 1) AND CLOSE / X_2 > 1 + 1 / 100;
    # X_45 := CLOSE < REF(CLOSE, 1) AND CLOSE / X_2 < 1 - 1 / 100;
    data['X_44'] = (data.close > REF(data.close, 1)) & ((data.close / data.X_2) > (1 + 1 / 100))
    data['X_45'] = (data.close < REF(data.close, 1)) & ((data.close / data.X_2) > (1 - 1 / 100))

    # X_46 := CROSS(SUM(X_44, 0), 0.5);
    # X_47 := CROSS(SUM(X_45, 0), 0.5);
    data['X_46'] = CROSS(SUM(data.X_44, 0), 0.5)
    data['X_47'] = CROSS(SUM(data.X_45, 0), 0.5)

    # X_48 := SUM(X_46, 0) * CROSS(COUNT(CLOSE < REF(CLOSE, 1), BARSLAST(X_46)), 0.5);
    # X_49 := SUM(X_47, 0) * CROSS(COUNT(CLOSE > REF(CLOSE, 1), BARSLAST(X_47)), 0.5);

    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_46)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        data_tmp = data.iloc[:i,:]
        if i==0:
            data.loc[i, 'tmp3'] = np.nan
            continue
        tmp = COUNT(data_tmp.close < REF(data_tmp.close, 1), data.tmp2[i])[-1]
        data.loc[i, 'tmp3'] = tmp
    data['X_48'] = SUM(data.X_46, 0) * CROSS(np.array(data.tmp3), 0.5)

    data['tmp'] = REF(data.close,1)
    data['tmp2'] = BARSLAST(data.X_47)
    data['tmp3'] = 0
    for i in range(data.shape[0]):
        tmp = COUNT(data.close > REF(data.close, 1), data.tmp2[i])[i]
        data.loc[i, 'tmp3'] = tmp
    data['X_49'] = SUM(data.X_47, 0) * CROSS(data.tmp3, 0.5)[1:]

    # X_50 := CONST(SUM(IF(X_48, REF(CLOSE, 1), DRAWNULL), 0));
    # X_51 := CONST(SUM(IF(X_49, REF(CLOSE, 1), DRAWNULL), 0));

    data['X_50'] = CONST(SUM(IF(data.X_48, REF(data.close, 1), np.nan), 0))
    data['X_51'] = CONST(SUM(IF(data.X_49, REF(data.close, 1), np.nan), 0))

    # DRAWICON(X_48, CLOSE * 1.002, 39);
    # DRAWICON(X_49, CLOSE * 0.9999, 38);

    # V1 := (C * 2 + H + L) / 4 * 10;
    # V2 := EMA(V1, 13) - EMA(V1, 34);
    # V3 := EMA(V2, 5);
    # V4 := 2 * (V2 - V3) * 5.5;

    data['V1'] = (data.close * 2 + data.high + data.low ) / 4 *10
    data['V2'] = EMA(data.V1,13) - EMA(data.V1,34)
    data['V3'] = EMA(data.V2,5)
    data['V4'] = 2*(data.V2-data.V3)*5.5

    # 主力进WW := IF(V4 >= 0, V4, 0);
    data['WW'] = IF(data.V4>=0,data.V4,0)
    # V11 := 3 * SMA((C - LLV(L, 55)) / (HHV(H, 55) - LLV(L, 55)) * 100, 5, 1) - 2 * SMA(SMA((C - LLV(L, 55)) / (HHV(H, 55) - LLV(L, 55)) * 100, 5, 1), 3, 1);
    data['V11'] = 3*SMA((data.close-LLV(data.low,55))/(HHV(data.high,55)-LLV(data.low,55))*100,5) - 2 * SMA(SMA((data.close-LLV(data.low,55))/(HHV(data.high,55)-LLV(data.low,55))*100,5),3)

    # 趋势线 := EMA(V11, 3);

    fig = plot_cand_volume(data, dt_breaks)

    return data, fig


data, fig = celve1()
st.plotly_chart(fig)
