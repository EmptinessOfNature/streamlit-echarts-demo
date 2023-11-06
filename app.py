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

def penxingdi(data):

    def LLV(x, n):
        return x.rolling(window=n).min()

    def HHV(x, n):
        return x.rolling(window=n).max()

    def SMA(close, n):
        weights = np.array(range(1, n + 1))
        sum_weights = np.sum(weights)
        res = close.rolling(window=n).apply(
            lambda x: np.sum(weights * x) / sum_weights, raw=False
        )
        return res

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
    data_dot = data[data.XG==1]
    data_dot.Code='XG'
    data=data.append(data_dot,ignore_index=True)
    # data.insert()
    # data.loc[data.XG == 1, 'Code'] = 'XG'
    # for i in range(data.shape[0]):
    #     if data.XG[i] ==1 :
    #         data.insert()
    print('5,30分钟盆形底部策略')
    return data[[
                            "dt",
                            "open",
                            "close",
                            "high",
                            "low",
                            "vol",
                            "cje",
                            "zxj",
                            "Code",
                        ]]

def main():
    st.title("股票交易回测123")
    client = ''

    with st.sidebar:
        st.header("Configuration")
        api_options = ("echarts", "pyecharts")
        selected_api = st.selectbox(
            label="Choose your preferred API:",
            options=api_options,
        )

        page_options = (
            list(ST_PY_DEMOS.keys())
            if selected_api == "pyecharts"
            else list(ST_DEMOS.keys())
        )
        selected_page = st.selectbox(
            label="Choose an example",
            options=page_options,
        )
        demo, url = (
            ST_DEMOS[selected_page]
            if selected_api == "echarts"
            else ST_PY_DEMOS[selected_page]
        )
        # 输入股票代码框
        stockCode = st.text_input("Stock Code:")
        conn = {"SC": stockCode}
        # 按钮
        if st.button("开始"):
            if len(stockCode) < 1:
                st.write("股票代码错误，请重试")
            else:
                st.write("加载股票中 " + str(stockCode) + " ...")
                try:
                    stock_data = ak.stock_us_hist_min_em(symbol=str(stockCode))
                    stock_data["Code"] = "分时图"
                    data_list = stock_data.values.tolist()
                    data_list.insert(
                        0,
                        [
                            "dt",
                            "open",
                            "close",
                            "high",
                            "low",
                            "vol",
                            "cje",
                            "zxj",
                            "Code",
                        ],
                    )
                    f = open("./data/stock_input_code_fenshi.json", "w")
                    f.write(str(data_list).replace("'", '"'))
                    f.close()
                    st.write("数据加载完成!")
                    st.title("股票交易回测" + stockCode)
                except:
                    st.write("股票代码错误，请重试")
         # 按钮
        if st.button("盈透"):

            print('按下button盈透'+str(datetime.now()))
            if len(stockCode) < 1:
                st.write("股票代码错误，请重试")
            st.write('使用盈透数据，数据加载中'+stockCode)
            if client == '':
                client = SimpleClient('127.0.0.1', 7497, 3)
                print('新建client')
            client.reqCurrentTime()
            if os.path.isfile('data/historicalData.json'):
                os.remove('data/historicalData.json')

            contract = Contract()
            # contract.symbol = "TSLA"
            contract.symbol = stockCode
            contract.secType = "STK"
            contract.currency = "USD"
            # In the API side, NASDAQ is always defined as ISLAND in the exchange field
            contract.exchange = "ISLAND"
            now = datetime.now().strftime("%Y%m%d %H:%M:%S")
            req_id = int(datetime.now().strftime("%Y%m%d"))
            client.reqHistoricalData(req_id, contract, now, '1 w', '1 min', 'MIDPOINT', False, 1, False, [])
            time.sleep(5)
            print('断开client')
            client.disconnect()
            ret='[["dt", "open", "close", "high", "low", "vol", "cje", "zxj", "Code"],'+open('data/historicalData.json').readline()[:-1]+']'
            with open('data/historicalData_j.json','w') as f:
                f.write(ret)

            st.write(stockCode + " 数据加载完成!")
            with open("./data/historicalData_j.json") as f:
                raw_data = json.load(f)
                data=pd.DataFrame(raw_data[1:],columns=raw_data[0])
                data=penxingdi(data)
                print(data)
            data_list = data.values.tolist()
            data_list.insert(
                0,
                [
                    "dt",
                    "open",
                    "close",
                    "high",
                    "low",
                    "vol",
                    "cje",
                    "zxj",
                    "Code",
                ],
            )
            f = open("./data/historicalData_dot.json", "w")
            f.write(str(data_list).replace("'", '"'))
            f.close()
            st.write(stockCode + " 数据处理完成!")


        if selected_api == "echarts":
            st.caption(
                """ECharts demos are extracted from https://echarts.apache.org/examples/en/index.html, 
            by copying/formattting the 'option' json object into st_echarts.
            Definitely check the echarts example page, convert the JSON specs to Python Dicts and you should get a nice viz."""
            )
        if selected_api == "pyecharts":
            st.caption(
                """Pyecharts demos are extracted from https://github.com/pyecharts/pyecharts-gallery,
            by copying the pyecharts object into st_pyecharts. 
            Pyecharts is still using ECharts 4 underneath, which is why the theming between st_echarts and st_pyecharts is different."""
            )

    demo()

    sourcelines, _ = inspect.getsourcelines(demo)
    with st.expander("Source Code"):
        st.code(textwrap.dedent("".join(sourcelines[1:])))
    st.markdown(f"Credit: {url}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Streamlit ECharts Demo", page_icon=":chart_with_upwards_trend:"
    )
    main()
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by 李鹏宇 </h6>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="margin-top: 0.75em;"><a href="https://www.buymeacoffee.com" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a></div>',
            unsafe_allow_html=True,
        )
