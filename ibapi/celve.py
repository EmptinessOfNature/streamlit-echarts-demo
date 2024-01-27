import akshare as ak
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from MyTT import *
import ibapi.indicator as ind


def celve_5min(data, stockCode,stockDate,show_1d=1,is_huice=0):
    if show_1d:
        if is_huice==0:
            # 数据只保留stockDate的17:00到次日的09:00
            stockDate_plus1 = stockDate[:3] + str(int(stockDate[3:5]) + 1)
            print(stockDate_plus1)
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
        elif is_huice==1:
            # 回测数据dt标注有问题，过0点之后，仍为同一天
            stockDate_plus1 = str(int(stockDate[3:5]) + 1) if int(stockDate[3:5])>=10 else '0'+str(int(stockDate[3:5]) + 1)
            data_1d = data[
                (
                        (data["dt"].str.contains(stockDate))
                        & (
                                (data["dt"].str[11:13] + data["dt"].str[14:16]).astype(int)
                                >= 2230
                        )
                )
                | (
                        (data["dt"].str.contains(stockDate))
                        & (
                                (data["dt"].str[11:13] + data["dt"].str[14:16]).astype(int)
                                <= 500
                        )
                )
                ]
    else:
        data_1d = data.reset_index(drop=True)
    # dt_all = pd.date_range(
    #     start=data_1d["dt"].iloc[0], end=data_1d["dt"].iloc[-1], freq="1min"
    # )
    # dt_all = [d.strftime("%Y-%m-%d %H:%M:%S") for d in dt_all]
    # dt_breaks = list(set(dt_all) - set(data_1d["dt"]))
    dt_breaks=''

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

    if is_huice==1:
        # 回测数据的dt有问题，过了24点仍然是原来的日期，故需要再返回之前进行处理
        data_1d_before_0 = data_1d[
            (
                    (data_1d["dt"].str.contains(stockDate))
                    & (
                            (data_1d["dt"].str[11:13] + data_1d["dt"].str[14:16]).astype(int)
                            >= 2230
                    )
            )]
        data_1d_after_0 = data_1d[
            (
                    (data_1d["dt"].str.contains(stockDate))
                    & (
                            (data_1d["dt"].str[11:13] + data_1d["dt"].str[14:16]).astype(int)
                            <= 500
                    )
            )
            ]
        data_1d_after_0.loc[:,'dt'] = data_1d_after_0['dt'].str[:8]+stockDate_plus1+data_1d_after_0['dt'].str[10:]
        data_1d = pd.concat([data_1d_before_0,data_1d_after_0]).reset_index(drop=True)
    if is_huice==1:
        data_1d,data_op_detail_1d = huice_1d(data_1d,zhiying_perc=0.005)
    fig = plot_cand_volume(data_1d, dt_breaks)

    return data_1d,data_op_detail_1d, fig

def signal_1(data: pd.DataFrame):
    n = 5
    m = 15
    # X_1:=CLOSE;  {收盘价}
    # X_2:=ZSTJJ; {分时均价}
    # X_3:=SUM(CLOSE*VOL,0)/SUM(VOL,0);
    # X_14:=REF(CLOSE,1);
    x1 = data["close"]
    x2 = (data["close"] * data["volume"]).cumsum() / data["volume"].cumsum()
    x3 = (data["close"] * data["volume"]).cumsum() / data["volume"].cumsum()
    x14 = data["close"].shift(1)

    # X_15:=SMA(MAX(CLOSE-X_14,0),14,1)/SMA(ABS(CLOSE-X_14),14,1)*100;
    # X_16:=CROSS(80,X_15);
    # X_17:=FILTER(X_16,60) AND CLOSE/X_3>1.005;

    x15 = (
        ind.SMA(ind.MAX(data["close"] - x14, 0).value, 14, 1).value
        / ind.SMA(abs(data["close"] - x14), 14, 1).value
        * 100
    )
    x16 = ind.CROSS(80, x15).value
    x17 = ind.AND(ind.FILTER(x16, 60).value, (data["close"] / x3 > 1.005)).value

    # X_18:=CROSS(X_15,20);
    # X_19:=FILTER(X_18,60) AND CLOSE/X_3<0.995;
    x18 = ind.CROSS(x15, 20).value
    x19 = ind.AND(ind.FILTER(x18, 60).value, (data["close"] / x3 < 0.995)).value

    # DRAWICON(X_19,CLOSE*0.997,13);
    # DRAWICON(X_17, CLOSE * 1.003, 41);
    icon_13 = x19
    icon_41 = x17

    # X_20:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+N/1000;
    # X_21:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-N/1000;
    # X_22:=CROSS(SUM(X_20,0),0.5);
    # X_23:=CROSS(SUM(X_21,0),0.5);
    x20 = (data["close"] > data["close"].shift(1)) & (data["close"] / x2 > 1 + n / 1000)
    x21 = (data["close"] < data["close"].shift(1)) & (data["close"] / x2 < 1 - n / 1000)
    x22 = ind.CROSS(x20.cumsum(), 0.5).value
    x23 = ind.CROSS(x21.cumsum(), 0.5).value

    # SUM(X_22,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_22)),0.5);
    x24 = (
        ind.SUM(x22, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] < data["close"].shift(1), ind.BARSLAST(x22).value
            ).value,
            0.5,
        ).value
    )
    # X_25:=SUM(X_23,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_23)),0.5);
    x25 = (
        ind.SUM(x23, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] > data["close"].shift(1), ind.BARSLAST(x23).value
            ).value,
            0.5,
        ).value
    )

    # X1:CONST(SUM(IF(X_24,REF(CLOSE,1),DRAWNULL),0)),DOTLINE,COLORYELLOW;
    # Z1:CONST(SUM(IF(X_25,REF(CLOSE,1),DRAWNULL),0)),DOTLINE,COLORGREEN;
    l1 = ind.CONST(ind.SUM(ind.IF(x24, data["close"].shift(1), ind.NA).value, 0).value).value
    l2 = ind.CONST(ind.SUM(ind.IF(x25, data["close"].shift(1), ind.NA).value, 0).value).value

    # X_26:=CROSS(SUM(X_20 AND CLOSE>X1*(1+1/100),0),0.5);
    x26 = ind.CROSS((x20 & (data["close"] > l1 * (1 + 1 / 100))).cumsum(), 0.5).value
    # X_27:=CROSS(SUM(X_21 AND CLOSE<Z1*(1-1/100),0),0.5);
    x27 = ind.CROSS((x21 & (data["close"] < l2 * (1 - 1 / 100))).cumsum(), 0.5).value
    # X_28:=SUM(X_26,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_26)),0.5);
    x28 = (
        ind.SUM(x26, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] < data["close"].shift(1), ind.BARSLAST(x26).value
            ).value,
            0.5,
        ).value
    )
    # X_29:=SUM(X_27,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_27)),0.5);
    x29 = (
        ind.SUM(x27, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] > data["close"].shift(1), ind.BARSLAST(x27).value
            ).value,
            0.5,
        ).value
    )

    # X2:CONST(SUM(IF(X_28,REF(CLOSE,1),DRAWNULL),0)),COLORWHITE;
    # Z2:CONST(SUM(IF(X_29,REF(CLOSE,1),DRAWNULL),0)),COLORGREEN;
    l3 = ind.CONST(ind.SUM(ind.IF(x28, data["close"].shift(1), ind.NA).value, 0).value).value
    l4 = ind.CONST(ind.SUM(ind.IF(x29, data["close"].shift(1), ind.NA).value, 0).value).value

    # DRAWICON(X_25, REF(CLOSE * 0.9999, 1), 1);
    # DRAWICON(X_29, REF(CLOSE * 0.9999, 1), 34);
    # DRAWICON(X_24, REF(CLOSE * 1.0015, 1), 2);
    # DRAWICON(X_28, REF(CLOSE * 1.0015, 1), 35);

    icon_1 = x25
    icon_34 = x29
    icon_2 = x24
    icon_35 = x28

    # X_30:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+M/1000;
    x30 = (data["close"] > data["close"].shift(1)) & (data["close"] / x2 > 1 + m / 1000)
    # X_31:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-M/1000;
    x31 = (data["close"] < data["close"].shift(1)) & (data["close"] / x2 < 1 - m / 1000)
    # X_32:=CROSS(SUM(X_30,0),0.5);
    x32 = ind.CROSS(ind.SUM(x30, 0).value, 0.5).value
    # X_33:=CROSS(SUM(X_31,0),0.5);
    x33 = ind.CROSS(ind.SUM(x31, 0).value, 0.5).value

    # X_34:=SUM(X_32,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_32)),0.5);
    x34 = (
        ind.SUM(x32, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] < data["close"].shift(1), ind.BARSLAST(x32).value
            ).value,
            0.5,
        ).value
    )
    # X_35:=SUM(X_33,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_33)),0.5);
    x35 = (
        ind.SUM(x33, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] > data["close"].shift(1), ind.BARSLAST(x33).value
            ).value,
            0.5,
        ).value
    )

    # X_36:=CONST(SUM(IF(X_34,REF(CLOSE,1),DRAWNULL),0));
    x36 = ind.CONST(ind.SUM(ind.IF(x34, data["close"].shift(1), np.nan).value, 0).value).value
    # X_37:=CONST(SUM(IF(X_35,REF(CLOSE,1),DRAWNULL),0));
    x37 = ind.CONST(ind.SUM(ind.IF(x35, data["close"].shift(1), np.nan).value, 0).value).value

    # X_38:=CROSS(SUM(X_30 AND CLOSE>X_36*1.02,0),0.5);
    x38 = ind.CROSS(ind.SUM(x30 & (data["close"] > x36 * 1.02), 0).value, 0.5).value
    # X_39:=CROSS(SUM(X_31 AND CLOSE<X_37*0.98,0),0.5);
    x39 = ind.CROSS(ind.SUM(x31 & (data["close"] < x37 * 0.98), 0).value, 0.5).value

    # X_40:=SUM(X_38,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_38)),0.5);
    x40 = (
        ind.SUM(x38, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] < data["close"].shift(1), ind.BARSLAST(x38).value
            ).value,
            0.5,
        ).value
    )
    # X_41:=SUM(X_39,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_39)),0.5);
    x41 = (
        ind.SUM(x39, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] > data["close"].shift(1), ind.BARSLAST(x39).value
            ).value,
            0.5,
        ).value
    )

    # X_42:=CONST(SUM(IF(X_40,REF(CLOSE,1),DRAWNULL),0));
    x42 = ind.CONST(ind.SUM(ind.IF(x40, data["close"].shift(1), np.nan).value, 0).value).value
    # X_43:=CONST(SUM(IF(X_41,REF(CLOSE,1),DRAWNULL),0));
    x43 = ind.CONST(ind.SUM(ind.IF(x41, data["close"].shift(1), np.nan).value, 0).value).value

    # DRAWICON(X_40,CLOSE*1.002,12);
    icon_12 = x40
    # DRAWICON(X_41,CLOSE*0.998,11);
    icon_11 = x41

    # X_44:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+1/100;
    x44 = (data["close"] > data["close"].shift(1)) & (data["close"] / x2 > 1 + 1 / 100)
    # X_45:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-1/100;
    x45 = (data["close"] < data["close"].shift(1)) & (data["close"] / x2 < 1 - 1 / 100)
    # X_46:=CROSS(SUM(X_44,0),0.5);
    x46 = ind.CROSS(ind.SUM(x44, 0).value, 0.5).value
    # X_47:=CROSS(SUM(X_45,0),0.5);
    x47 = ind.CROSS(ind.SUM(x45, 0).value, 0.5).value

    # X_48:=SUM(X_46,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_46)),0.5);
    x48 = (
        ind.SUM(x46, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] < data["close"].shift(1), ind.BARSLAST(x46).value
            ).value,
            0.5,
        ).value
    )

    # X_49:=SUM(X_47,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_47)),0.5);
    x49 = (
        ind.SUM(x47, 0).value
        * ind.CROSS(
            ind.COUNT(
                data["close"] > data["close"].shift(1), ind.BARSLAST(x47).value
            ).value,
            0.5,
        ).value
    )

    # X_50:=CONST(SUM(IF(X_48,REF(CLOSE,1),DRAWNULL),0));
    x50 = ind.CONST(ind.SUM(ind.IF(x48, data["close"].shift(1), np.nan).value, 0).value)
    # X_51:=CONST(SUM(IF(X_49,REF(CLOSE,1),DRAWNULL),0));
    x51 = ind.CONST(ind.SUM(ind.IF(x49, data["close"].shift(1), np.nan).value, 0).value)
    # DRAWICON(X_48,CLOSE*1.002,39);
    # DRAWICON(X_49,CLOSE*0.9999,38);
    icon_39 = x48
    icon_38 = x49

    # V1:=(C*2+H+L)/4*10;
    # V2:=EMA(V1,13)-EMA(V1,34);
    # V3:=EMA(V2,5); V4:=2*(V2-V3)*5.5;
    # 主力进WW:=IF(V4>=0,V4,0);
    # V11:=3*SMA((C-LLV(L,55))/(HHV(H,55)-LLV(L,55))*100,5,1)-2*SMA(SMA((C-LLV(L,55))/(HHV(H,55)-LLV(L,55))*100,5,1),3,1);
    # 趋势线:=EMA(V11,3);
    # 见顶清仓:=FILTER(趋势线>90 AND 趋势线<REF(趋势线,1) AND 主力进WW<REF(主力进WW,1),8);
    # DRAWTEXT( 见顶清仓,C*0.9999,'逃'),COLORYELLOW;

    icon = (
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
    )

    return icon

def huice_1d(data,zhiying_perc):
    data['buy_signal'] = (1*data['icon_1'] + 2*data['icon_38']+ 3*data['icon_34']+ 4*data['icon_13']+ 5*data['icon_11'])
    data['sell_signal'] = (1*data['icon_2'] + 2*data['icon_39']+ 3*data['icon_35']+ 4*data['icon_12']+ 5*data['icon_41'])

    long_index = data[data['buy_signal'] >= 1].index
    short_index = data[data['sell_signal'] >= 1].index

    long_end_index = []
    short_end_index = []
    for i in long_index:
        high = data.iloc[i]['close']
        for j in range(len(data)-i-2):
            if (int(data.iloc[i + j]['dt'][11:13]) >= 3) and (int(data.iloc[i + j]['dt'][14:16]) >= 50):
                # 如果到最后10分钟，则直接卖掉
                long_end_index.append(i + j)
                break
            elif data.iloc[i + j]['sell_signal'] >= 1:
                # 出现卖出信号则卖
                long_end_index.append(i + j)
                break
            else:
                # 计算止盈
                cur_price = data.iloc[i + j]['close']
                if cur_price > high:
                    high = cur_price
                if high / cur_price - 1 >= zhiying_perc:
                    long_end_index.append(i + j)
                    break
    # data['long_end'] = 0
    # for i in long_end_index:
    #     data.loc[i,'long_end']=1
    data_profit = data.copy(deep=True)
    data_profit['profit'] = 0
    data_profit['long_end'] = 0
    long_buy = data_profit.iloc[long_index].reset_index(drop=True)
    long_sell = data_profit.iloc[long_end_index].reset_index(drop=True)

    for i in range(len(long_sell)):
        buy_price = long_buy.iloc[i]['close']
        sell_price = long_sell.iloc[i]['close']
        profit = sell_price/buy_price - 1
        long_sell.loc[i,'profit'] = profit
        long_sell.loc[i,'long_end'] = 1
        if i==0:
            data_op_detail=pd.concat([long_buy.iloc[[i]],long_sell.iloc[[i]]])
        else:
            data_op_detail=pd.concat([data_op_detail,long_buy.iloc[[i]],long_sell.iloc[[i]]])

    return data,data_op_detail

def plot_cand_volume(data, dt_breaks):
    # Create subplots and mention plot grid size
    fig = make_subplots(
        rows=5,
        cols=1,
        # row_heights=[1,0.5,0.5,0.5],
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(""),
        row_width=[1, 1, 1, 1, 6],
    )
    # 绘制k数据
    # fig.add_trace(go.Candlestick(x=data["dt"], open=data["open"], high=data["high"],
    #                              low=data["low"], close=data["close"], name=""),
    #               row=1, col=1
    #               )

    # 走势图
    fig.add_trace(
        go.Scatter(x=data["dt"], y=data["close"], showlegend=True, name="分时图"),
        row=1,
        col=1,
    )

    # # 盆形底买入信号
    # data_new = data[data["XG_IN"] == 1]
    # fig.add_trace(go.Scatter(
    #     x=data_new["dt"],
    #     y=data_new["XG_IN"] * data_new["close"] * 1.01, mode='markers', text='👇', marker={"color": "green"},showlegend=True,name='盆型底'), row=1,
    #     col=1)  # 散点大小
    #
    # data_new2 = data[data["XG_OUT"] * -1 == 1]
    # fig.add_trace(go.Scatter(
    #     x=data_new2["dt"],
    #     y=data_new2["XG_OUT"] * data_new2["close"] * (-0.99), mode='markers', text='^', marker={"color": "red"},showlegend=True,name='盆型顶'), row=1,
    #     col=1)  # 散点大小

    data_nm24 = data[data["icon_2"] == 1]
    fig.add_trace(
        go.Scatter(
            x=data_nm24["dt"],
            y=data_nm24["icon_2"] * data_nm24["close"] * (1.001),
            mode="markers",
            text="2",
            marker={"color": "red"},
            showlegend=True,
            name="icon_2",
        ),
        row=1,
        col=1,
    )  # 散点大小

    data_nm25 = data[data["icon_1"] == 1]
    fig.add_trace(
        go.Scatter(
            x=data_nm25["dt"],
            y=data_nm25["icon_1"] * data_nm25["close"] * (1.001),
            mode="markers",
            text="1",
            marker={"color": "green"},
            showlegend=True,
            name="icon_1",
        ),
        row=1,
        col=1,
    )  # 散点大小
    data_nm_dict = {}
    for icon in (
        "icon_11",
        "icon_12",
        "icon_13",
        "icon_34",
        "icon_35",
        "icon_38",
        "icon_39",
        "icon_41",
    ):
        data_nm_dict[icon] = data[data[icon] == 1]
        fig.add_trace(
            go.Scatter(
                x=data_nm_dict[icon]["dt"],
                y=data_nm_dict[icon][icon] * data_nm_dict[icon]["close"] * (1.001),
                mode="markers",
                text="2",
                marker={"color": "red"},
                showlegend=True,
                name=icon,
            ),
            row=1,
            col=1,
        )  # 散点大小

    # 绘制成交量数据
    fig.add_trace(
        go.Bar(x=data["dt"], y=data["vol"], showlegend=True, name="成交量"), row=2, col=1
    )

    # 绘制策略点5分钟盆型底
    fig.add_trace(
        go.Scatter(x=data["dt"], y=data["JW_30"], showlegend=True, name="JW_30"),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(x=data["dt"], y=data["JW_5"], showlegend=True, name="JW_5"),
        row=3,
        col=1,
    )
    fig.update_yaxes(range=[-10, 110], row=3, col=1)


    fig.add_trace(go.Bar(x=data["dt"], y=[1]*data.shape[0],marker=dict(color=data["DING_30min"]),showlegend=False,name='5min盆型'), row=4, col=1)
    # fig.add_trace(go.Bar(x=data["dt"], y=[data["XG_5min"],data["XG_30min"]], showlegend=False), row=3, col=1)

    # fig.add_trace(go.Bar(x=data["dt"], y=data["XG_30min"],marker=dict(color=data["XG_30min"]), showlegend=False), row=4, col=1)
    fig.add_trace(go.Bar(x=data["dt"], y=[1]*data.shape[0], marker=dict(color=data["DI_30min"]),showlegend=False,name='30min盆型'),
                  row=5, col=1)

    # 绘制策略点

    # fig.add_trace(
    #     go.Scatter(x=data["dt"], y=data["JW"], showlegend=True,name='5min盆型曲线'), row=5, col=1
    # )

    fig.update_yaxes(
        showline=True,
        linecolor="black",
        linewidth=1,
        gridwidth=1,
        title={"font": {"size": 18}, "text": "", "standoff": 10},
        automargin=True,
    )

    # fig.update_xaxes(
    #     title_text='dt',
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
            # dict(bounds=[8, 16], pattern="hour"),
            dict(bounds=[9, 17], pattern="hour"),
            # dict(bounds=[6, 1], pattern="day of week"),
        ],
    )
    hovertext = []  # 添加悬停信息

    for i in range(len(data["close"])):  # <br>表示
        hovertext.append(
            "时间: " + str(data["dt"][i]) + "<br>价格: " + str(data["close"][i])
        )

    fig.update_layout(hovermode="x unified")

    return fig


if __name__ == "__main__":
    import json
    data_path_ready = '../data_hist/TSLA.json'
    with open(data_path_ready) as f:
        raw_data = json.load(f)
        data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
    data_op_details = ''
    for i in range(1,6):
        for j in range(1,30):
            date_mm = '0'+str(i) if i <10 else str(i)
            date_dd = '0'+str(j) if j <10 else str(j)
            date = date_mm+'-'+date_dd
            print(date)
            try:
                _,data_op_detail,__ = celve_5min(data, stockCode='TSLA', stockDate=date, show_1d=1, is_huice=1)
                print(data_op_detail)
                if not isinstance(data_op_details,pd.DataFrame):
                    data_op_details = data_op_detail
                else:
                    data_op_details = pd.concat([data_op_details,data_op_detail])
            except:
                print('no data')
    data_op_details=data_op_details.reset_index(drop=True)
    data_op_details.to_csv('./data_op_details.csv')

    # _,data_op_detail,__ = celve_5min(data,stockCode='TSLA',stockDate='01-03',show_1d=1,is_huice=1)
    # print(data_op_detail)

