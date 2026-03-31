"""
chanpy — chan.py 的 Python 导入代理包。

chan.py 内部模块用裸导入（from Common.xxx），需要 chanpy/ 在 sys.path 中。
本文件负责：
1. 将 chanpy/ 加入 sys.path（仅一次）
2. 重新导出常用类，确保外部代码和 chanpy 内部拿到的是同一个类对象

外部代码应这样导入：
    from chanpy import CChan, CChanConfig, CKLine_Unit
    from chanpy import KL_TYPE, BI_DIR, BSP_TYPE, FX_TYPE, MACD_ALGO, AUTYPE, DATA_SRC, DATA_FIELD
    from chanpy import CTime
"""
import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
if _dir not in sys.path:
    sys.path.insert(0, _dir)

# 重新导出核心类（与 chanpy 内部共享同一个类对象，避免 isinstance 失败）
from Chan import CChan                          # noqa: E402,F401
from ChanConfig import CChanConfig              # noqa: E402,F401
from KLine.KLine_Unit import CKLine_Unit        # noqa: E402,F401
from KLine.KLine_List import CKLine_List        # noqa: E402,F401
from Common.CEnum import (                      # noqa: E402,F401
    KL_TYPE, BI_DIR, BSP_TYPE, FX_TYPE, MACD_ALGO,
    AUTYPE, DATA_SRC, DATA_FIELD, SEG_TYPE,
    KLINE_DIR, BI_TYPE, TREND_TYPE,
)
from Common.CTime import CTime                  # noqa: E402,F401
from Common.func_util import kltype_lt_day      # noqa: E402,F401
from Common.ChanException import CChanException # noqa: E402,F401
from Bi.Bi import CBi                           # noqa: E402,F401
from Seg.Seg import CSeg                        # noqa: E402,F401
from ZS.ZS import CZS                          # noqa: E402,F401
from BuySellPoint.BS_Point import CBS_Point     # noqa: E402,F401

__all__ = [
    "CChan", "CChanConfig", "CKLine_Unit", "CKLine_List",
    "KL_TYPE", "BI_DIR", "BSP_TYPE", "FX_TYPE", "MACD_ALGO",
    "AUTYPE", "DATA_SRC", "DATA_FIELD", "SEG_TYPE",
    "KLINE_DIR", "BI_TYPE", "TREND_TYPE",
    "CTime", "kltype_lt_day", "CChanException",
    "CBi", "CSeg", "CZS", "CBS_Point",
]
