import typing

import pandas as pd
import numpy as np

"""
指标函数只接受两种数据类型：
    - 时间序列数据: pd.Series，不带索引默认日期从小到大，索引必须一致对齐
    - 时点常数: int, float, np.nan, np.inf
    使用Sn代表时间序列数据，使用Cn代表时点常数数据，使用Xn代表接受两种数据类型
"""

# Define Constant
ZERO = 0
UNIT = 1
NA = np.nan  # bool值应该为false
INF = np.inf

# Define Data Type
S = typing.TypeVar('S', bound=pd.Series)
C = typing.TypeVar('C', int, float)
X = typing.Generic[S, C]


def to_series(*values):
    """将values内所有的values全部转为series，index对齐"""
    indexes = None
    new_values = []
    for v in values:
        if isinstance(v, pd.Series):
            indexes = v.index
            break
    if indexes is not None:
        for v in values:
            if not isinstance(v, pd.Series):
                new_values.append(pd.Series([v] * len(indexes), index=indexes))
            else:
                new_values.append(v)
        return tuple(new_values)
    else:
        raise ValueError("There is no 'pd.Series' type.")


class Indicator(object):
    _value = None

    def _run(self):
        ...

    @property
    def value(self):
        return self._value


class AND(Indicator):

    def __init__(self, x1: X, x2: X):
        """
        x1 & x2

        Parameters
        ----------
        x1: 任意时序或者常数
        x2: 任意时序或者常数
        """
        self._x1 = x1
        self._x2 = x2
        self._x1, self._x2 = to_series(self._x1, self._x2)
        self._run()

    def _run(self):
        self._x1 = self._x1.apply(lambda x: bool(x))
        self._x2 = self._x2.apply(lambda x: bool(x))
        self._value = self._x1 & self._x2


class BARSLAST(Indicator):


    def __init__(self, s1: S):
        """
        上一次条件成立到现在的天数，上一次为1到现在的天数

        Parameters
        ----------
        s1
        """
        self._s1 = s1
        self._run()

    def _run(self):
        self._value = self._s1.rolling(window=len(self._s1), min_periods=1).apply(
            lambda x: x.values.tolist()[::-1].index(1) if 1 in x.values else np.nan
        )


class CONST(Indicator):
    """取最后一个值为常数"""

    def __init__(self, s1: S):
        self._s1 = s1
        self._run()

    def _run(self):
        self._value = pd.Series(self._s1.values.tolist()[-1], index=self._s1.index)


class COUNT(Indicator):

    def __init__(self,
                 s1: S,
                 x1: X,
                 ):
        """
        统计N周期中满足X条件的周期数,若N<0则从第一个有效值开始.

        Parameters
        ----------
        s1
        x1
        """
        self._s1 = s1
        self._x1 = x1
        self._s1, self._x1 = to_series(self._s1, self._x1)
        self._run()

    def _run(self):
        self._x1 = self._x1.where(lambda x: x > 0, 0)
        self._value = self._s1.rolling(window=len(self._s1), min_periods=1).apply(
            lambda x: x[int(-self._x1.values[len(x) - 1]):].sum() if len(x) >= self._x1.values[len(x) - 1] else x.sum())



class CROSS(Indicator):
    """
    A从下方上穿B，返回1
    """

    def __init__(self,
                 x1,
                 x2,
                 ):
        """
        x1从下方上穿x2，返回1

        Parameters
        ----------
        x1: 时序数据
        x2: 时序数据
        """
        self._x1 = x1
        self._x2 = x2
        self._x1, self._x2 = to_series(self._x1, self._x2)
        self._run()

    def _run(self):
        self._value = AND(
            self._x1 > self._x2,  # 当期x1 > x2
            REF(self._x1 < self._x2, 1).value  # 前期x1 < x2
        ).value
        self._value = self._value.where(pd.notna, 0)


class EMA(Indicator):

    def __init__(self,
                 s1: S,
                 c1: C,
                 ):
        """
        EMA Indicator

        Parameters
        ----------
        s1: 时序数据
        c1: 窗体长度

        Notes:
            四舍五入后与同花顺一致
        """
        self._s1 = s1
        self._c1 = c1
        self._run()

    def _run(self):
        self._value = self._s1.ewm(span=self._s1, adjust=False).mean()


class FILTER(Indicator):

    def __init__(self, s1: S, c1: C):
        """
        s1成立后c1窗口内都返回0

        Parameters
        ----------
        s1: 布尔条件
        c1: 窗口大小
        """
        self._s1 = s1
        self._c1 = int(c1)
        self._run()

    def _run(self):
        if 1 in self._s1.values:
            idx = self._s1.tolist().index(1)
            imp = pd.Series(([1] + [0] * self._c1) * int(np.ceil((len(self._s1) - idx) / (self._c1 + 1)))).loc[
                  : len(self._s1)]
            self._value = pd.Series(self._s1.loc[:idx - 1].values.tolist() + imp.values.tolist()) * self._s1

        else:
            self._value = self._s1


class IF(Indicator):

    def __init__(self, x1: X, x2: X, x3: X):
        """
        x2 if x1 else x3

        Parameters
        ----------
        x1: 布尔条件
        x2: 为真返回x2
        x3：为假返回x3
        """
        self._x1 = x1
        self._x2 = x2
        self._x3 = x3
        self._x1, self._x2, self._x3 = to_series(self._x1, self._x2, self._x3)
        self._run()

    def _run(self):
        self._value = pd.Series(index=self._x1.index)
        self._value.loc[self._x1[self._x1 == True].index,] = self._x2.loc[self._x1 == True]
        self._value.loc[self._x1[self._x1 == False].index,] = self._x3.loc[self._x1 == False]


class MACD(Indicator):

    def __init__(self,
                 s1: S,
                 c1: C = 12,
                 c2: C = 26,
                 c3: C = 9,
                 ):
        """
        MACD Indicator

        Parameters
        ----------
        s1: 时序数据
        c1: short window
        c2: long window
        c3: mid window
        """
        self._s1 = s1
        self._c1 = c1
        self._c2 = c2
        self._c3 = c3
        self._run()

    def _run(self):
        self._sema = EMA(self._s1, self._c1).value
        self._lema = EMA(self._s1, self._c2).value
        self._dif = self._sema - self._lema
        self._dea = EMA(self._dif, self._c3).value
        self._value = 2 * (self._dif - self._dea)

    @property
    def sema(self):
        return self._sema

    @property
    def lema(self):
        return self._lema

    @property
    def dif(self):
        return self._dif

    @property
    def dea(self):
        return self._dea


class MAX(Indicator):
    def __init__(self, x1: X, x2: X):
        self._x1 = x1
        self._x2 = x2
        self._x1, self._x2 = to_series(self._x1, self._x2)
        self._run()

    def _run(self):
        self._value = self._x1.where(lambda x: x > self._x2, self._x2)


class REF(Indicator):
    def __init__(self, s1: S, c1: C = 1):
        self._s1 = s1
        self._c1 = c1
        self._run()

    def _run(self):
        self._value = self._s1.shift(self._c1)


class SMA(Indicator):

    def __init__(self,
                 s1: S,
                 c1: C = 3,
                 c2: C = 1,
                 ):
        """
        SMA Indicator

        Parameters
        ----------
        s1
        c1: N
        c2: M

        Notes:
            四舍五入后与通达信一致
        """
        self._s1 = s1
        self._c1 = c1
        self._c2 = c2
        self._r = self._c2 / self._c1
        self._run()

    def _run(self):
        # 修改初始值
        self._s1.iloc[0] = self._s1.values[0] / self._r
        self._value = self._s1.rolling(window=self._s1.shape[0], min_periods=1).apply(
            lambda x: (self._r * ((1 - self._r) ** np.arange(0, len(x))[::-1]) * x).sum()
        )


class SUM(Indicator):

    def __init__(self, s1: S, c1: C):
        """

        Parameters
        ----------
        s1: 时序数据，可以包含空值
        c1: 窗口大小，当为0时，表示全部累计加总
        """
        self._s1 = s1
        self._c1 = c1
        self._run()

    def _run(self):
        if self._c1 == 0:
            self._value = pd.Series(np.nancumsum(self._s1))
        else:
            self._value = self._s1.rolling(window=self._c1, min_periods=1).apply(lambda x: np.nansum(x))


if __name__ == '__main__':
    a = pd.Series([1, 1, 0, 1, 1, 1, 0])
    b = pd.Series([1, 1, 1, 0, 0, -1, 1])
    c = pd.Series([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    v = SUM(a, 0).value
    print(v)
