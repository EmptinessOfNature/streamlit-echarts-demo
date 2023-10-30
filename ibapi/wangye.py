import random

import streamlit as st
import time
import streamlit as st
from bokeh.plotting import figure
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from pandas.core.frame import DataFrame

# import time
# now = time.time()
# timeArray = time.localtime(now)
# otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
# print(now)
# print(otherStyleTime)
# otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)


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
        c = {'date': time_stamp, "open": prices_open, "high": prices_high, "low": prices_low, "close": prices_close}
        data = DataFrame(c)
        data['date'] = data['date'].apply(lambda x: datetime.datetime.utcfromtimestamp(int(x)))
        for line in lines:
            if "x00169" not in line:
                continue
            time_stamp.append(line.split("\\x00")[6])
            prices_open.append(line.split("\\x00")[7])
            prices_close.append(line.split("\\x00")[8])
            prices_high.append(line.split("\\x00")[9])
            prices_low.append(line.split("\\x00")[10])

        p = figure(
            title='simple line example',
            x_axis_label='x',
            y_axis_label='y')

        p.line(time_stamp, prices_low, legend_label='Trend', line_width=2)

        st.bokeh_chart(p, use_container_width=True)

