#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: market@sandquant.com
# Copyright © 2020-present SandQuant Group. All Rights Reserved.

import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import indicator as i


def signal_1(data: pd.DataFrame):
    n = 5
    m = 15
    # X_1:=CLOSE;  {收盘价}
    # X_2:=ZSTJJ; {分时均价}
    # X_3:=SUM(CLOSE*VOL,0)/SUM(VOL,0);
    # X_14:=REF(CLOSE,1);
    x1 = data['close']
    x2 = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
    x3 = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()
    x14 = data['close'].shift(1)

    # X_15:=SMA(MAX(CLOSE-X_14,0),14,1)/SMA(ABS(CLOSE-X_14),14,1)*100;
    # X_16:=CROSS(80,X_15);
    # X_17:=FILTER(X_16,60) AND CLOSE/X_3>1.005;

    x15 = i.SMA(i.MAX(data['close'] - x14, 0).value, 14, 1).value / i.SMA(abs(data['close'] - x14), 14, 1).value * 100
    x16 = i.CROSS(80, x15).value
    x17 = i.AND(i.FILTER(x16, 60).value, (data['close'] / x3 > 1.005)).value

    # X_18:=CROSS(X_15,20);
    # X_19:=FILTER(X_18,60) AND CLOSE/X_3<0.995;
    x18 = i.CROSS(x15, 20).value
    x19 = i.AND(i.FILTER(x18, 60).value, (data['close'] / x3 < 0.995)).value

    # DRAWICON(X_19,CLOSE*0.997,13);
    # DRAWICON(X_17, CLOSE * 1.003, 41);
    icon_13 = x19
    icon_41 = x17

    # X_20:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+N/1000;
    # X_21:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-N/1000;
    # X_22:=CROSS(SUM(X_20,0),0.5);
    # X_23:=CROSS(SUM(X_21,0),0.5);
    x20 = (data['close'] > data['close'].shift(1)) & (data['close'] / x2 > 1 + n / 1000)
    x21 = (data['close'] < data['close'].shift(1)) & (data['close'] / x2 < 1 - n / 1000)
    x22 = i.CROSS(x20.cumsum(), 0.5).value
    x23 = i.CROSS(x21.cumsum(), 0.5).value

    # SUM(X_22,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_22)),0.5);
    x24 = i.SUM(x22, 0).value * i.CROSS(
        i.COUNT(data['close'] < data['close'].shift(1), i.BARSLAST(x22).value).value,
        0.5
    ).value
    # X_25:=SUM(X_23,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_23)),0.5);
    x25 = i.SUM(x23, 0).value * i.CROSS(
        i.COUNT(data['close'] > data['close'].shift(1), i.BARSLAST(x23).value).value,
        0.5
    ).value

    # X1:CONST(SUM(IF(X_24,REF(CLOSE,1),DRAWNULL),0)),DOTLINE,COLORYELLOW;
    # Z1:CONST(SUM(IF(X_25,REF(CLOSE,1),DRAWNULL),0)),DOTLINE,COLORGREEN;
    l1 = i.CONST(i.SUM(i.IF(x24, data['close'].shift(1), i.NA).value, 0).value).value
    l2 = i.CONST(i.SUM(i.IF(x25, data['close'].shift(1), i.NA).value, 0).value).value

    # X_26:=CROSS(SUM(X_20 AND CLOSE>X1*(1+1/100),0),0.5);
    x26 = i.CROSS((x20 & (data['close'] > l1 * (1 + 1 / 100))).cumsum(), 0.5).value
    # X_27:=CROSS(SUM(X_21 AND CLOSE<Z1*(1-1/100),0),0.5);
    x27 = i.CROSS((x21 & (data['close'] < l2 * (1 - 1 / 100))).cumsum(), 0.5).value
    # X_28:=SUM(X_26,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_26)),0.5);
    x28 = i.SUM(x26, 0).value * i.CROSS(
        i.COUNT(data['close'] < data['close'].shift(1), i.BARSLAST(x26).value).value,
        0.5
    ).value
    # X_29:=SUM(X_27,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_27)),0.5);
    x29 = i.SUM(x27, 0).value * i.CROSS(i.COUNT(data['close'] > data['close'].shift(1), i.BARSLAST(x27).value).value,
                                        0.5).value

    # X2:CONST(SUM(IF(X_28,REF(CLOSE,1),DRAWNULL),0)),COLORWHITE;
    # Z2:CONST(SUM(IF(X_29,REF(CLOSE,1),DRAWNULL),0)),COLORGREEN;
    l3 = i.CONST(i.SUM(i.IF(x28, data['close'].shift(1), i.NA).value, 0).value).value
    l4 = i.CONST(i.SUM(i.IF(x29, data['close'].shift(1), i.NA).value, 0).value).value

    # DRAWICON(X_25, REF(CLOSE * 0.9999, 1), 1);
    # DRAWICON(X_29, REF(CLOSE * 0.9999, 1), 34);
    # DRAWICON(X_24, REF(CLOSE * 1.0015, 1), 2);
    # DRAWICON(X_28, REF(CLOSE * 1.0015, 1), 35);

    icon_1 = x25
    icon_34 = x29
    icon_2 = x24
    icon_35 = x28

    # X_30:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+M/1000;
    x30 = (data['close'] > data['close'].shift(1)) & (data['close'] / x2 > 1 + m / 1000)
    # X_31:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-M/1000;
    x31 = (data['close'] < data['close'].shift(1)) & (data['close'] / x2 < 1 - m / 1000)
    # X_32:=CROSS(SUM(X_30,0),0.5);
    x32 = i.CROSS(i.SUM(x30, 0).value, 0.5).value
    # X_33:=CROSS(SUM(X_31,0),0.5);
    x33 = i.CROSS(i.SUM(x31, 0).value, 0.5).value

    # X_34:=SUM(X_32,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_32)),0.5);
    x34 = i.SUM(x32, 0).value * i.CROSS(i.COUNT(data['close'] < data['close'].shift(1), i.BARSLAST(x32).value).value,
                                        0.5).value
    # X_35:=SUM(X_33,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_33)),0.5);
    x35 = i.SUM(x33, 0).value * i.CROSS(i.COUNT(data['close'] > data['close'].shift(1), i.BARSLAST(x33).value).value,
                                        0.5).value

    # X_36:=CONST(SUM(IF(X_34,REF(CLOSE,1),DRAWNULL),0));
    x36 = i.CONST(i.SUM(i.IF(x34, data['close'].shift(1), np.nan).value, 0).value).value
    # X_37:=CONST(SUM(IF(X_35,REF(CLOSE,1),DRAWNULL),0));
    x37 = i.CONST(i.SUM(i.IF(x35, data['close'].shift(1), np.nan).value, 0).value).value

    # X_38:=CROSS(SUM(X_30 AND CLOSE>X_36*1.02,0),0.5);
    x38 = i.CROSS(
        i.SUM(x30 & (data['close'] > x36 * 1.02), 0).value, 0.5
    ).value
    # X_39:=CROSS(SUM(X_31 AND CLOSE<X_37*0.98,0),0.5);
    x39 = i.CROSS(
        i.SUM(x31 & (data['close'] < x37 * 0.98), 0).value, 0.5
    ).value

    # X_40:=SUM(X_38,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_38)),0.5);
    x40 = i.SUM(x38, 0).value * i.CROSS(
        i.COUNT(data['close'] < data['close'].shift(1), i.BARSLAST(x38).value).value, 0.5).value
    # X_41:=SUM(X_39,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_39)),0.5);
    x41 = i.SUM(x39, 0).value * i.CROSS(
        i.COUNT(data['close'] > data['close'].shift(1), i.BARSLAST(x39).value).value, 0.5).value

    # X_42:=CONST(SUM(IF(X_40,REF(CLOSE,1),DRAWNULL),0));
    x42 = i.CONST(i.SUM(i.IF(x40, data['close'].shift(1), np.nan).value, 0).value).value
    # X_43:=CONST(SUM(IF(X_41,REF(CLOSE,1),DRAWNULL),0));
    x43 = i.CONST(i.SUM(i.IF(x41, data['close'].shift(1), np.nan).value, 0).value).value

    # DRAWICON(X_40,CLOSE*1.002,12);
    icon_12 = x40
    # DRAWICON(X_41,CLOSE*0.998,11);
    icon_11 = x41

    # X_44:=CLOSE>REF(CLOSE,1) AND CLOSE/X_2>1+1/100;
    x44 = (data['close'] > data['close'].shift(1)) & (data['close'] / x2 > 1 + 1 / 100)
    # X_45:=CLOSE<REF(CLOSE,1) AND CLOSE/X_2<1-1/100;
    x45 = (data['close'] < data['close'].shift(1)) & (data['close'] / x2 < 1 - 1 / 100)
    # X_46:=CROSS(SUM(X_44,0),0.5);
    x46 = i.CROSS(i.SUM(x44, 0).value, 0.5).value
    # X_47:=CROSS(SUM(X_45,0),0.5);
    x47 = i.CROSS(i.SUM(x45, 0).value, 0.5).value

    # X_48:=SUM(X_46,0)*CROSS(COUNT(CLOSE<REF(CLOSE,1),BARSLAST(X_46)),0.5);
    x48 = i.SUM(x46, 0).value * i.CROSS(
        i.COUNT(data['close'] < data['close'].shift(1), i.BARSLAST(x46).value).value, 0.5).value

    # X_49:=SUM(X_47,0)*CROSS(COUNT(CLOSE>REF(CLOSE,1),BARSLAST(X_47)),0.5);
    x49 = i.SUM(x47, 0).value * i.CROSS(
        i.COUNT(data['close'] > data['close'].shift(1), i.BARSLAST(x47).value).value, 0.5).value

    # X_50:=CONST(SUM(IF(X_48,REF(CLOSE,1),DRAWNULL),0));
    x50 = i.CONST(
        i.SUM(i.IF(x48, data['close'].shift(1), np.nan).value, 0).value
    )
    # X_51:=CONST(SUM(IF(X_49,REF(CLOSE,1),DRAWNULL),0));
    x51 = i.CONST(
        i.SUM(i.IF(x49, data['close'].shift(1), np.nan).value, 0).value
    )
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

    icon = (icon_1, icon_2, icon_11, icon_12, icon_13, icon_34, icon_35, icon_38, icon_39, icon_41)

    return icon


if __name__ == '__main__':
    import tda

    data = tda.get_prices(symbol='AAPL', frequency=1, frequencyType='minute', extend=False)

    icon_1, icon_2, icon_11, icon_12, icon_13, icon_34, icon_35, icon_38, icon_39, icon_41 = signal_1(data)
    icons = dict(zip(
        ['1', '2', '11', '12', '13', '34', '35', '38', '39', '41'],
        [icon_1, icon_2, icon_11, icon_12, icon_13, icon_34, icon_35, icon_38, icon_39, icon_41]
    ))
    # data.set_index('datetime', inplace=True)
    data['close'].plot(kind='line', color='#0b3558', figsize=(10, 6))
    for icon_name, icon in icons.items():
        a = icon[icon == 1]
        if len(a) > 0:
            for i in a.index:
                plt.annotate(icon_name, xy=(i, data['close'].loc[i]), xytext=(i, data['close'].loc[i]), color='red', weight='bold')
    plt.title(f'AAPL')
    plt.show()
