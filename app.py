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


def main():
    st.title("NBNB123")
    client = ""

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
        stockDate = st.text_input("Stock Date（例：01-10）")
        # 按钮
        # 5、30分钟
        if st.button("盈透5、30min盆形底"):
            # v2盈透历史分时图

            print("按下button盈透" + str(datetime.now()))
            if len(stockCode) < 1:
                st.write("股票代码错误，请重试")
            st.write("使用盈透数据，数据加载中" + stockCode)
            # if os.path.isfile("data/historicalData.json"):
            #     os.remove("data/historicalData.json")

            contract = Contract()
            # contract.symbol = "TSLA"
            contract.symbol = stockCode
            contract.secType = "STK"
            contract.currency = "USD"
            # In the API side, NASDAQ is always defined as ISLAND in the exchange field
            contract.exchange = "ISLAND"
            now = datetime.now().strftime("%Y%m%d %H:%M:%S")
            # import pytz
            # now = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%Y%m%d %H:%M:%S")
            # now = '20231119 12:00:00 US/Eastern'

            # req_id = int(datetime.now().strftime("%Y%m%d"))

            stock_dict = {'TSLA':'1001','MSFT':'1002','NVDA':'1003','AAPL':'1004','AMZN':'1005','TSM':'1006','NFLX':'1007','GOOG':'1008',
                          'META':'1009','ASML':'1010','ARKK':'1011','PDD':'1012','NQ':'1013'}

            req_id = int(stock_dict[stockCode]+stockDate.replace('-',''))
            print('req_id',req_id)
            data_path = 'data/' + str(req_id) + '.json'
            data_path_ready = 'data_ready/' + str(req_id) + '.json'
            if not os.path.isfile(data_path):
                print("数据不存在，读取得到")
                if client=='':
                    client = SimpleClient("127.0.0.1", 7497, 3)
                    client.reqCurrentTime()
                    print("新建client")
                client.reqHistoricalData(
                    req_id, contract, now, "1 w", "1 min", "TRADES", False, 1, False, []
                )
                # client.reqHistoricalData(req_id, contract, now, '1 w', '1 min', 'ADJUSTED_LAST', False, 1, False, [])
                time.sleep(5)
                print("断开client")
                client.disconnect()
            else:
                print('数据已存在，直接读取')
            ret = (
                '[["dt", "open", "close", "high", "low", "vol", "cje", "zxj", "Code"],'
                + open(data_path).readline()[:-1]
                + "]"
            )
            with open(data_path_ready, "w") as f:
                f.write(ret)

            st.write(stockCode + " 数据加载完成!")
            with open(data_path_ready) as f:
                raw_data = json.load(f)
                data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            # v3分时图


            data,data_op_detail_1d, fig = celve_5min(data,stockCode,stockDate,show_1d=1,is_huice=0)

            data_path_calc = 'data_calc/' + str(stockCode)+str(stockDate) + '.csv'
            data_op_detail_1d.to_csv(data_path_calc)

        if st.button("回测"):
            data_path_ready = './data_hist/TSLA.json'
            with open(data_path_ready) as f:
                raw_data = json.load(f)
                data = pd.DataFrame(raw_data[1:], columns=raw_data[0])
            # data=data[(data["dt"].str[0:4]=='2023') & (data["dt"].str[5:7].astype(int)==12)& (data["dt"].str[8:10].astype(int)>=27)]
            data, fig = celve_5min(data, stockCode, stockDate, show_1d=1,is_huice=1)

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
    # v2分时图
    # demo()

    # v3分时图
    st.plotly_chart(fig)

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
