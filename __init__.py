"""
缠论技术分析框架 (Chan.py)

基于缠论理论的股票技术分析工具，提供完整的缠论计算、买卖点识别、策略开发等功能。

主要功能：
- 缠论基本元素计算（分形、笔、线段、中枢、买卖点）
- 多级别联立计算和区间套分析
- 自定义买卖点策略开发
- 机器学习模型集成
- 数据源对接（支持多种数据源）
- 可视化绘图功能

作者：Vespa314
版本：1.0.0
许可证：MIT
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Vespa314"
__email__ = ""
__license__ = "MIT"

# 导入核心类
try:
    from .Chan import CChan
    from .ChanConfig import CChanConfig
except ImportError:
    from Chan import CChan
    from ChanConfig import CChanConfig

# 导入枚举类
try:
    from .Common.CEnum import (
        AUTYPE,
        DATA_SRC,
        KL_TYPE,
        BI_DIR,
        BI_TYPE,
        SEG_TYPE,
        BSP_TYPE,
        TREND_TYPE,
        LEFT_SEG_METHOD,
        FX_TYPE,
        MACD_ALGO,
        KLINE_DIR,
        FX_CHECK_METHOD,
        TREND_LINE_SIDE,
        DATA_FIELD,
    )
except ImportError:
    from Common.CEnum import (
        AUTYPE,
        DATA_SRC,
        KL_TYPE,
        BI_DIR,
        BI_TYPE,
        SEG_TYPE,
        BSP_TYPE,
        TREND_TYPE,
        LEFT_SEG_METHOD,
        FX_TYPE,
        MACD_ALGO,
        KLINE_DIR,
        FX_CHECK_METHOD,
        TREND_LINE_SIDE,
        DATA_FIELD,
    )

# 导入异常类
try:
    from .Common.ChanException import CChanException, ErrCode
except ImportError:
    from Common.ChanException import CChanException, ErrCode

# 导入时间类
try:
    from .Common.CTime import CTime
except ImportError:
    from Common.CTime import CTime

# 导入K线相关类
try:
    from .KLine.KLine_Unit import CKLine_Unit
    from .KLine.KLine_List import CKLine_List
    from .KLine.KLine import CKLine
except ImportError:
    from KLine.KLine_Unit import CKLine_Unit
    from KLine.KLine_List import CKLine_List
    from KLine.KLine import CKLine

# 导入笔相关类
try:
    from .Bi.Bi import CBi
    from .Bi.BiList import CBiList
    from .Bi.BiConfig import CBiConfig
except ImportError:
    from Bi.Bi import CBi
    from Bi.BiList import CBiList
    from Bi.BiConfig import CBiConfig

# 导入线段相关类
try:
    from .Seg.Seg import CSeg
    from .Seg.SegListComm import CSegListComm
    from .Seg.SegListChan import CSegListChan
    from .Seg.SegConfig import CSegConfig
except ImportError:
    from Seg.Seg import CSeg
    from Seg.SegListComm import CSegListComm
    from Seg.SegListChan import CSegListChan
    from Seg.SegConfig import CSegConfig

# 导入中枢相关类
try:
    from .ZS.ZS import CZS
    from .ZS.ZSList import CZSList
    from .ZS.ZSConfig import CZSConfig
except ImportError:
    from ZS.ZS import CZS
    from ZS.ZSList import CZSList
    from ZS.ZSConfig import CZSConfig

# 导入买卖点相关类
try:
    from .BuySellPoint.BS_Point import CBS_Point
    from .BuySellPoint.BSPointList import CBSPointList
    from .BuySellPoint.BSPointConfig import CBSPointConfig
except ImportError:
    from BuySellPoint.BS_Point import CBS_Point
    from BuySellPoint.BSPointList import CBSPointList
    from BuySellPoint.BSPointConfig import CBSPointConfig

# 导入数学计算类
try:
    from .Math.MACD import CMACD
    from .Math.BOLL import BollModel
    from .Math.TrendModel import CTrendModel
    from .Math.Demark import CDemarkEngine
    from .Math.RSI import RSI
    from .Math.KDJ import KDJ
except ImportError:
    from Math.MACD import CMACD
    from Math.BOLL import BollModel
    from Math.TrendModel import CTrendModel
    from Math.Demark import CDemarkEngine
    from Math.RSI import RSI
    from Math.KDJ import KDJ

# 导入绘图相关类
try:
    from .Plot.PlotDriver import CPlotDriver
    from .Plot.AnimatePlotDriver import CAnimateDriver
except ImportError:
    from Plot.PlotDriver import CPlotDriver
    from Plot.AnimatePlotDriver import CAnimateDriver

# 导入数据API相关类
try:
    from .DataAPI.CommonStockAPI import CCommonStockApi
except ImportError:
    from DataAPI.CommonStockAPI import CCommonStockApi

# 导入工具函数
try:
    from .Common.func_util import (
        check_kltype_order,
        kltype_lte_day,
        _parse_inf,
    )
except ImportError:
    from Common.func_util import (
        check_kltype_order,
        kltype_lte_day,
        _parse_inf,
    )

# 定义__all__，控制from chan import *的行为
__all__ = [
    # 核心类
    "CChan",
    "CChanConfig",
    
    # 枚举类
    "AUTYPE",
    "DATA_SRC", 
    "KL_TYPE",
    "BI_DIR",
    "BI_TYPE",
    "SEG_TYPE",
    "BSP_TYPE",
    "TREND_TYPE",
    "LEFT_SEG_METHOD",
    "FX_TYPE",
    "MACD_ALGO",
    "KLINE_DIR",
    "FX_CHECK_METHOD",
    "TREND_LINE_SIDE",
    "DATA_FIELD",
    
    # 异常类
    "CChanException",
    "ErrCode",
    
    # 时间类
    "CTime",
    
    # K线相关
    "CKLine_Unit",
    "CKLine_List", 
    "CKLine",
    
    # 笔相关
    "CBi",
    "CBiList",
    "CBiConfig",
    
    # 线段相关
    "CSeg",
    "CSegListComm",
    "CSegListChan",
    "CSegConfig",
    
    # 中枢相关
    "CZS",
    "CZSList",
    "CZSConfig",
    
    # 买卖点相关
    "CBS_Point",
    "CBSPointList",
    "CBSPointConfig",
    
    # 数学计算
    "CMACD",
    "BollModel",
    "CTrendModel",
    "CDemarkEngine",
    "RSI",
    "KDJ",
    
    # 绘图
    "CPlotDriver",
    "CAnimateDriver",
    
    # 数据API
    "CCommonStockApi",
    
    # 工具函数
    "check_kltype_order",
    "kltype_lte_day",
    "_parse_inf",
    
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

# 包级别的配置
def get_version():
    """获取版本号"""
    return __version__

def get_author():
    """获取作者信息"""
    return __author__

def get_license():
    """获取许可证信息"""
    return __license__

# 包初始化完成
