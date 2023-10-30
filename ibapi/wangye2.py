import random

import streamlit as st
import time
import streamlit as st
from bokeh.plotting import figure
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from pandas.core.frame import DataFrame
import pandas as pd

# def get_trading_date():
#     # 获取市场的交易时间
#     trade_date = ak.tool_trade_date_hist_sina()['trade_date']
#     trade_date = [d.strftime("%Y-%m-%d") for d in trade_date]
#     return trade_date

def plot_cand_volume(data, dt_breaks):
    # Create subplots and mention plot grid size
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=('', '成交量'),
                        row_width=[0.2, 0.7])

    # 绘制k数据
    fig.add_trace(go.Candlestick(x=data["date"], open=data["open"], high=data["high"],
                                 low=data["low"], close=data["close"], name=""),
                  row=1, col=1
                  )

    # 绘制成交量数据
    fig.add_trace(go.Bar(x=data['date'], y=data['volume'], showlegend=False), row=2, col=1)

    fig.update_xaxes(
        title_text='date',
        rangeslider_visible=True,  # 下方滑动条缩放
        rangeselector=dict(
            # 增加固定范围选择
            buttons=list([
                dict(count=1, label='1M', step='month', stepmode='backward'),
                dict(count=6, label='6M', step='month', stepmode='backward'),
                dict(count=1, label='1Y', step='year', stepmode='backward'),
                dict(count=1, label='YTD', step='year', stepmode='todate'),
                dict(step='all')])))

    # Do not show OHLC's rangeslider plot
    fig.update(layout_xaxis_rangeslider_visible=False)
    # 去除休市的日期，保持连续
    fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])

    return fig

with st.empty():
    while True:
        time.sleep(5)
        # Get new data here


        fread=open('./ui_database.txt','r')

        lines=fread.readlines()

        time_stamp = []
        prices_open = []
        prices_close = []
        prices_high = []
        prices_low = []

        for line in lines:
            if "x00169" not in line:
                continue
            time_stamp.append(line.split("\\x00")[6])
            prices_open.append(line.split("\\x00")[7])
            prices_close.append(line.split("\\x00")[8])
            prices_high.append(line.split("\\x00")[9])
            prices_low.append(line.split("\\x00")[10])

        c = {'volume':prices_open,'date': time_stamp, "open": prices_open, "high": prices_high, "low": prices_low, "close": prices_close}
        data = DataFrame(c)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.utcfromtimestamp(int(x)))

        dt_all = pd.date_range(start=data['date'].iloc[0], end=data['date'].iloc[-1])
        dt_all = [d.strftime("%Y-%m-%d") for d in dt_all]
        # dt_breaks = list(set(dt_all) - set(get_trading_date()))
        # 绘制 复杂k线图

        fig = plot_cand_volume(data, list(set([])))
        print(fig)
        st.plotly_chart(fig)