import random
import pandas as pd
import time
import numpy as np
import akshare as ak
import datetime
import json
import math

def get_stock_price(share, start_date="20230301", end_date="20230918"):
    # 获取个股行情数据
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=share, period="daily", start_date=start_date,
                                            end_date=end_date)  # adjust="qfq"
    return stock_zh_a_hist_df
#
# data = get_stock_price(share='000792')
# data = data.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'})
# print("====data===")
# print(data)

def calcCurYK(price, cur_chicang):
    #计算盈亏，根据当前的收盘价与持仓数量
    cur_chicang_tmp = cur_chicang.replace('{', '').replace('}', '').split(',')
    yingli = 0
    gu_num = 0
    for chicangstr in cur_chicang_tmp:
        buy_in_price = float(chicangstr.split(":")[0])
        buy_in_num = float(chicangstr.split(":")[1])
        yingli += (price-buy_in_price)*buy_in_num
        gu_num += buy_in_num
    return yingli, gu_num



# input, 股票id，持仓现状（dict 买入价格，个数），现金，action(dataframe - > time，stress)
def get_money_gogogo(share_id, cur_dict, cash, action):
    # 1.获取股票信息
    data = get_stock_price(share=share_id)
    data = data.rename(columns={'日期': 'date', '开盘': 'open', '收盘': 'close', '最高': 'high', '最低': 'low', '成交量': 'volume'})
    data[['date']] = data[['date']].astype('string')
    # 3.初始化结果表，data加上 cash，cur_dict, cur_dict_yingkui, action,action详情
    data["现金"], data["当前持仓"], data["当前持仓盈亏"] = cash, str(cur_dict), 0
    action[['date']] = action[['date']].astype('string')
    # 4.给data join action
    data_action = pd.merge(data, action, how='outer', on='date')
    data_action["决策强度"]=data_action["决策强度"].fillna(0)
    data_action["决策详情"] = "以xx单价购入/卖出xx股"
    print("====data_action====")
    print(data_action)
    data_action_res = data_action
    # 5.遍历data，更新买入or卖出价格（不能超过持仓）、持仓、持仓盈亏（action点为0，其他均更新）
    for index, row in data_action.iterrows():
        # print(index, row["当前持仓"], row["当前持仓盈亏"], row["决策强度"], row["close"])
        cur_cash = float(data_action_res["现金"][index - 1] if index>0 else data_action_res["现金"][index])
        cur_chicang = data_action_res["当前持仓"][index - 1] if index>0 else data_action_res["当前持仓"][index]
        decision = row["决策强度"]
        price = row["close"]
        if decision==0:
            yingkui,_ = calcCurYK(price, cur_chicang)
            data_action_res["当前持仓盈亏"][index]=yingkui
            data_action_res["决策详情"][index]="无"
            data_action_res["当前持仓"][index]=cur_chicang
            data_action_res["现金"][index]=cur_cash
        else:
            yingkui,gu_num = calcCurYK(price, cur_chicang)
            data_action_res["当前持仓盈亏"][index] = yingkui
            if decision<0:
                # 卖出 份额的强度
                num = abs(math.floor(gu_num*decision))
                data_action_res["决策详情"][index] = str("以"+str(price)+"单价卖出" + str(num) +"股")
                trade_money = cur_chicang.replace("}","")+","+str(-1*price)+":"+str(num)+"}"
                data_action_res["当前持仓"][index] = trade_money
                data_action_res["现金"][index] = cur_cash + num*price
            else:
                # 买入现金的强度
                num = math.floor(cur_cash * decision/price)
                data_action_res["决策详情"][index] = str("以" + str(price) + "单价买入" +str(num)+"股" )
                trade_money = cur_chicang.replace("}", "") + "," + str(price) + ":" + str(num) + "}"
                data_action_res["当前持仓"][index] = trade_money
                data_action_res["现金"][index] = cur_cash - num * price
    return data_action_res



share_id = '000001'
cur_dict = {}
cur_dict[90] = 100
cur_dict[80] = 40
# cur_dict = {"90":100,"80":40} #90块钱买了100股，80块钱买了40股
cash = 100000
action =  pd.DataFrame({
    "date":["2023-03-02","2023-03-07","2023-09-13"],
    "决策强度":[-0.5,-0.2,0.1]
})
res = get_money_gogogo(share_id, cur_dict, cash, action)
print(res)