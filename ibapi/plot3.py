import akshare as ak
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np

def get_stock_price(share, start_date="20230815", end_date="20230816"):
    # 获取个股行情数据
    # stock_zh_a_hist_df = ak.stock_zh_a_hist_min_em(symbol=share, start_date=start_date,
    #                                                       end_date=end_date, period='1', adjust='')
    # stock_zh_a_hist_df = ak.stock_zh_a_minute(symbol=share, period='1', adjust='qfq')
    stock_zh_a_hist_df = ak.stock_us_hist_min_em(symbol="105.TQQQ")
    return stock_zh_a_hist_df


def get_trading_date():
    # 获取市场的交易时间
    trade_date = ak.tool_trade_date_hist_sina()['trade_date']
    trade_date = [d.strftime("%Y-%m-%d %H:%M:%S") for d in trade_date]
    return trade_date


def plot_cand_volume(data, data_5, dt_breaks):
    # Create subplots and mention plot grid size
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(''),
                        row_width=[1,1,1,1])

    # 绘制k数据
    # fig.add_trace(go.Candlestick(x=data["date"], open=data["open"], high=data["high"],
    #                              low=data["low"], close=data["close"], name=""),
    #               row=1, col=1
    #               )

    # 走势图
    fig.add_trace(go.Scatter(
        x=data["date"],
        y=data["close"]),row=1, col=1)

    data_new = data_5[data_5["XG_IN"] == 1]
    fig.add_trace(go.Scatter(
        x=data_new["date"],
        y=data_new["XG_IN"]*data_new["close"]*1.02, mode='text',text='⛛',marker={"color":"red"}), row=1, col=1) # 散点大小

    data_new2 = data_5[data_5["XG_OUT"]*-1 == 1]
    fig.add_trace(go.Scatter(
        x=data_new2["date"],
        y=data_new2["XG_OUT"]*data_new2["close"]*(-0.98), mode='text',text='🔺',marker={"color":"green"}), row=1, col=1) # 散点大小

    # 绘制成交量数据
    fig.add_trace(go.Bar(x=data['date'], y=data['volume'], showlegend=False), row=2, col=1)


    # 绘制策略点
    fig.add_trace(go.Bar(x=data_5['date'], y=data_5['XG'], showlegend=False), row=3, col=1)

    fig.add_trace(go.Scatter(x=data_5['date'], y=data_5['JW'], showlegend=False), row=4, col=1)


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
    fig.update_xaxes(tickformat="%Y-%m-%d %H:%M:%S", rangebreaks=[dict(bounds=[4, 21.5], pattern="hour"),dict(bounds=[6,1], pattern="day of week")])
    hovertext = []  # 添加悬停信息

    for i in range(len(data['close'])):  # <br>表示
        hovertext.append('时间: ' + str(data['date'][i]) + '<br>价格: ' + str(data['close'][i]))

    fig.update_layout(hovermode="x unified")

    return fig


def SMA(close, n):
    weights = np.array(range(1, n+1))
    sum_weights = np.sum(weights)
    res = close.rolling(window=n).apply(lambda x: np.sum(weights*x) / sum_weights, raw=False)
    return res

def LLV(x,n):
    return x.rolling(window=n).min()

def HHV(x,n):
    return x.rolling(window=n).max()

def celve1():
    save_flag=1
    if save_flag:
        data = get_stock_price(share='sh000001', start_date="2023-08-15 00:00:00", end_date="2023-08-17 20:59:00")
        data.to_csv('./sh000001_minute.csv')
        print('数据保存完成')
    else:
        print('读取本地csv')
        data = pd.read_csv('./sh000001_minute.csv')
    data = data.rename(
        columns={'时间': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'})
        # columns = {'day': 'date'})
    data['open'] = data['open'].astype('float')
    data['close'] = data['close'].astype('float')
    data['high'] = data['high'].astype('float')
    data['low'] = data['low'].astype('float')
    data['volume'] = data['volume'].astype('float')
    # 取固定dt的数据
    data = data[data['date'] >= '2023-08-11 08:00:00']
    dt_all = pd.date_range(start=data['date'].iloc[0], end=data['date'].iloc[-1],freq='1min')
    dt_all = [d.strftime("%Y-%m-%d %H:%M:%S") for d in dt_all]
    dt_breaks = list(set(dt_all) - set(data['date']))
    # 绘制 复杂k线图

    # 获取5min数据
    dt_all_5min = pd.date_range(start=data['date'].iloc[0], end=data['date'].iloc[-1],freq='5min')
    dt_all_5min = [d.strftime("%Y-%m-%d %H:%M:%S") for d in dt_all_5min]
    data_5min = data.loc[data['date'].isin(dt_all_5min)]


    # 买入点判断
    ne=45
    m1e=15
    m2e=15
    data_5min['RSVM'] = (data_5min['close']-LLV(data_5min['low'],ne))/(HHV(data_5min['high'],ne)-LLV(data_5min['low'],ne))*100
    data_5min['KW'] = SMA(data_5min['RSVM'], m1e)
    data_5min['DW'] = SMA(data_5min['KW'],m2e)
    data_5min['JW'] = (3*data_5min['KW']-2*data_5min['DW'])
    data_5min['XG_IN'] = 1* (data_5min['JW']<0)


    # 卖出点判断
    ne=45
    m1e=15
    m2e=15
    data_5min['RSVM'] = (data_5min['close']-LLV(data_5min['low'],ne))/(HHV(data_5min['high'],ne)-LLV(data_5min['low'],ne))*100
    data_5min['KW'] = SMA(data_5min['RSVM'], m1e)
    data_5min['DW'] = SMA(data_5min['KW'],m2e)
    data_5min['JW'] = (3*data_5min['KW']-2*data_5min['DW'])
    data_5min['XG_OUT'] = -1 * (data_5min['JW']>100)

    data_5min['XG'] = data_5min['XG_IN']+data_5min['XG_OUT']

    fig = plot_cand_volume(data, data_5min, dt_breaks)

    return data,fig


data,fig = celve1()
st.plotly_chart(fig)




