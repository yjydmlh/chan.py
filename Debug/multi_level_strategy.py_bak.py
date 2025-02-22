import ssl

import requests
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, BSP_TYPE, DATA_SRC, FX_TYPE, KL_TYPE
import ccxt  # 直接从ccxt包中导入
import pandas as pd
from datetime import datetime, timedelta
import certifi
from binance.client import Client
from DataAPI.ccxt import CCXT



def multi_level_strategy(code, begin_time, end_time, data_src_type, lv_list, config):
    chans = {lv: CChan(
        code=code,
        begin_time=begin_time,
        end_time=end_time,
        data_src=data_src_type,
        lv_list=[lv],
        config=config,
        autype=AUTYPE.QFQ,
    ) for lv in lv_list}

    is_hold = False
    is_short = False
    last_buy_price = 1
    last_sell_price = None
    total_profit = 0
    for lv in lv_list:
        chan = chans[lv]
        for _ in chan.step_load():
            bsp_list = chan[-1].bs_point_lst if chan else []
            if not bsp_list:
                continue

            for bsp in bsp_list.bsp_iter():
                # 买入条件：底分型且买卖点类型为买入
                if bsp.is_buy :
                    last_buy_price = bsp.klu.close
                    print(f'{bsp.klu.time} Buy: {last_buy_price}')
                # 卖出条件：顶分型且买卖点类型为卖出
                elif not bsp.is_buy :
                    sell_price = bsp.klu.close
                    profit = (sell_price - last_buy_price) / last_buy_price * 100
                    total_profit += profit
                    print(f'{bsp.klu.time} Sell: {sell_price}, Profit: {profit:.2f}%')

    print(f'Total Profit: {total_profit:.2f}%')

if __name__ == "__main__":
    code = "BTC/USDT"
    begin_time = "2024-01-01"
    end_time = None
    data_src_type = DATA_SRC.CCXT  # 使用CCXT作为数据源
    lv_list = [KL_TYPE.K_60M]
    config = CChanConfig({
        "trigger_step": True,
        "divergence_rate": 0.8,
        "min_zs_cnt": 1,
    })
    # url = "https://api.binance.com/api/v3/exchangeInfo"
    # response = requests.get(url, verify=certifi.where())
    # print(response.json())
    # print(ssl.get_default_verify_paths())
    # print(certifi.__version__)
    # print(certifi.where())
    multi_level_strategy(code, begin_time, end_time, data_src_type, lv_list, config)
