import ssl
from datetime import datetime

import ccxt
import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager

from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from Common.func_util import kltype_lt_day, str2float
from KLine.KLine_Unit import CKLine_Unit

from .CommonStockAPI import CCommonStockApi

def create_ssl_context():
    context = ssl.create_default_context()
    # 使用 certifi 提供的 CA 文件
    context.load_verify_locations(certifi.where())

    # 如果有自签 CA，也可以加上:
    # context.load_verify_locations("path/to/custom_ca.crt")

    # 如果想禁用 TLS 1.0/1.1 之类，也可以在这里改 context.options
    # ...
    return context

class CustomSslAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context  # 把传进来的 ssl_context 赋给 self.ssl_context
        super().__init__(**kwargs)       # 初始化父类 HTTPAdapter

    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,  # 这里要和 __init__ 里同名
            **kwargs
        )

def create_session_with_ssl_context(context: ssl.SSLContext) -> requests.Session:
    session = requests.Session()
    adapter = CustomSslAdapter(ssl_context=context)
    session.mount("https://", adapter)
    return session

def GetColumnNameFromFieldList(fileds: str):
    _dict = {
        "time": DATA_FIELD.FIELD_TIME,
        "open": DATA_FIELD.FIELD_OPEN,
        "high": DATA_FIELD.FIELD_HIGH,
        "low": DATA_FIELD.FIELD_LOW,
        "close": DATA_FIELD.FIELD_CLOSE,
    }
    return [_dict[x] for x in fileds.split(",")]


class CCXT(CCommonStockApi):
    is_connect = None

    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=AUTYPE.QFQ):
        super(CCXT, self).__init__(code, k_type, begin_date, end_date, autype)

    def get_kl_data(self):
        fields = "time,open,high,low,close"
        ssl_ctx = create_ssl_context()
        my_session = create_session_with_ssl_context(ssl_ctx)
        exchange = ccxt.binance({
            'session': my_session,
                                 'enableRateLimit': True
                                    ,'options': {
                            'defaultType': 'future',  # fapi
                        } })
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
                item[4]
            ]
            yield CKLine_Unit(self.create_item_dict(item_data, GetColumnNameFromFieldList(fields)), autofix=True)

    def SetBasciInfo(self):
        pass

    @classmethod
    def do_init(cls):
        pass

    @classmethod
    def do_close(cls):
        pass

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
