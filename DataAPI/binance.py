from datetime import datetime
from typing import Iterable

from DataAPI.CommonStockAPI import CCommonStockApi
from DataAPI.ccxt import GetColumnNameFromFieldList
from KLine.KLine_Unit import CKLine_Unit

from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from Common.func_util import kltype_lt_day, str2float
import ccxt

class Binance(CCommonStockApi):
    is_connect = None

    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=AUTYPE.QFQ):
        super(CCXT, self).__init__(code, k_type, begin_date, end_date, autype)

    def get_kl_data(self) -> Iterable[CKLine_Unit]:
        fields = "time,open,high,low,close,volume"
        exchange = ccxt.binance()
        timeframe = self.__convert_type()
        since_date = exchange.parse8601(f'{self.begin_date}T00:00:00')
        data = exchange.fetch_ohlcv(self.code, timeframe, since=since_date)

        for item in data:
            time_obj = datetime.fromtimestamp(item[0] / 1000)
            time_str = time_obj.strftime('%Y-%m-%d %H:%M:%S')
            item_data = [
                time_str,
                item[1],
                item[2],
                item[3],
                item[4],
                item[5]
            ]
            yield CKLine_Unit(self.create_item_dict(item_data, GetColumnNameFromFieldList(fields)), autofix=True)

    def SetBasciInfo(self):
        try:
            market_info = self.exchange.load_markets()
            symbol_info = market_info.get(self.code)
            if symbol_info:
                self.name = symbol_info.get('symbol')
                self.is_stock = symbol_info.get('isSpot')  # 假设isSpot表示是否为现货市场
            else:
                raise Exception(f"Symbol {self.code} not found on Binance")
        except Exception as e:
            print(f"Failed to fetch basic info for {self.code}: {e}")

    @classmethod
    def do_init(cls):
        # 初始化连接
        cls.exchange = ccxt.binance()
        cls.is_connect = True

    @classmethod
    def do_close(cls):
        # 初始化连接
        cls.exchange = ccxt.binance()
        cls.is_connect = True

    def __convert_type(self):
        _dict = {
            KL_TYPE.K_DAY: '1d',
            KL_TYPE.K_WEEK: '1w',
            KL_TYPE.K_MON: '1M',
            KL_TYPE.K_5M: '5m',
            KL_TYPE.K_15M: '15m',
            KL_TYPE.K_30M: '30m',
            KL_TYPE.K_60M: '1h',
        }
        return _dict[self.k_type]

    def parse_time_column(self, inp):
        if len(inp) == 10:
            year = int(inp[:4])
            month = int(inp[5:7])
            day = int(inp[8:10])
            hour = minute = 0
        elif len(inp) == 17:
            year = int(inp[:4])
            month = int(inp[4:6])
            day = int(inp[6:8])
            hour = int(inp[8:10])
            minute = int(inp[10:12])
        elif len(inp) == 19:
            year = int(inp[:4])
            month = int(inp[5:7])
            day = int(inp[8:10])
            hour = int(inp[11:13])
            minute = int(inp[14:16])
        else:
            raise Exception(f"unknown time column from TradingView:{inp}")
        return CTime(year, month, day, hour, minute, auto=not kltype_lt_day(self.k_type))

    def create_item_dict(self, data, column_name):
        for i in range(len(data)):
            data[i] = self.parse_time_column(data[i]) if i == 0 else str2float(data[i])
        return dict(zip(column_name, data))
