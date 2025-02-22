from datetime import datetime

import numpy as np

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE


class TradingAccount:
    def __init__(self, initial_capital=100000):
        self.capital = initial_capital
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.max_drawdown = 0
        self.consecutive_loss = 0
        self.trade_history = []

    def update_drawdown(self, current_value):
        peak = max([th['value'] for th in self.trade_history] + [current_value])
        self.max_drawdown = min(self.max_drawdown, (current_value - peak) / peak)

    def check_risk(self):
        if self.max_drawdown <= -0.15:
            return False
        if self.consecutive_loss >= 3:
            return False
        return True


def calculate_atr(klines, period=14):
    """支持CKLine对象列表的ATR计算"""
    # 获取所有原始K线单元的价格数据
    high_lst = []
    low_lst = []
    close_lst = []
    for klc in klines:  # klc是CKLine对象
        for klu in klc.lst:  # klu是CKLine_Unit对象
            high_lst.append(klu.high)
            low_lst.append(klu.low)
            close_lst.append(klu.close)

    high = np.array(high_lst)
    low = np.array(low_lst)
    close = np.array(close_lst)

    # 计算真实波动范围（TR）
    tr = np.maximum(high[1:] - low[1:],
                    np.abs(high[1:] - close[:-1]),
                    np.abs(low[1:] - close[:-1]))
    return np.mean(tr[-period:]) if len(tr) >= period else np.nan


class EnhancedChanStrategy:
    def __init__(self, config):
        self.day_chan = CChan(
            code="BTC/USDT",
            begin_time="2015-01-01",
            end_time=None,
            data_src=DATA_SRC.CCXT,
            lv_list=[KL_TYPE.K_60M],
            config=config,
            autype=AUTYPE.QFQ,
        )

        self.hour_chan = CChan(
            code="BTC/USDT",
            begin_time="2015-01-01",
            end_time=None,
            data_src=DATA_SRC.CCXT,
            lv_list=[KL_TYPE.K_60M],
            config=config,
            autype=AUTYPE.QFQ,
        )

        self.account = TradingAccount()
        self.current_trend = 0  # 1: 上涨, -1: 下跌
        self.atr = 0

    def get_macd_data(self, chan):
        """从CChan实例获取MACD指标"""
        kl_list = chan[0]  # 获取对应级别的K线列表
        return {
            'dif': [kl.macd.DIF for kl in kl_list.klu_iter()],
            'dea': [kl.macd.DEA for kl in kl_list.klu_iter()],
            'hist': [kl.macd.macd for kl in kl_list.klu_iter()]
        }

    def detect_trend(self):
        """日线趋势判断修正版"""
        day_kl_list = self.day_chan[KL_TYPE.K_60M]
        if len(day_kl_list.bi_list) < 3:
            return 0

        zs_list = day_kl_list.zs_list
        last_bi = day_kl_list.bi_list[-1]
        macd_data = self.get_macd_data(self.day_chan)
        last_klc = day_kl_list[-1]  # 获取最后一个合并K线
        current_price = last_klc.lst[-1].close  # 从原始K线单元获取收盘价

        if last_bi.is_up and macd_data['hist'][-1] > 0:
            if any(current_price > zs.high for zs in zs_list[-2:]):  # 判断突破中枢上沿
                return 1
        elif not last_bi.is_up and macd_data['hist'][-1] < 0:
            if any(current_price < zs.low for zs in zs_list[-2:]):  # 判断跌破中枢下沿
                return -1
        return 0

    def find_third_bs_point(self):
        """小时线买卖点检测修正版"""
        hour_kl_list = self.hour_chan[KL_TYPE.K_60M]
        if not hour_kl_list.zs_list:
            return None

        last_zs = hour_kl_list.zs_list[-1]
        current_price = hour_kl_list[-1].lst[-1].close
        macd_data = self.get_macd_data(self.hour_chan)

        # 第三类买卖点判断
        if self.current_trend == 1:  # 多头
            if (current_price > last_zs.high and
                    macd_data['hist'][-1] > macd_data['hist'][-3] and
                    macd_data['dif'][-1] > macd_data['dea'][-1]):
                return ('buy', last_zs.high)
        elif self.current_trend == -1:  # 空头
            if (current_price < last_zs.low and
                    macd_data['hist'][-1] < macd_data['hist'][-3] and
                    macd_data['dif'][-1] < macd_data['dea'][-1]):
                return ('sell', last_zs.low)
        return None


    def calculate_position_size(self, stop_loss_pct):
        risk_capital = self.account.capital * 0.02
        return risk_capital / abs(stop_loss_pct)

    def execute_trade(self, signal):
        if not self.account.check_risk():
            return

        action, pivot = signal
        current_price = self.hour_chan[0][-1].lst[-1].close
        self.atr = calculate_atr(self.hour_chan[0].lst)

        if action == 'buy':
            stop_loss = pivot - self.atr
            stop_loss_pct = (current_price - stop_loss) / current_price
            position_size = self.calculate_position_size(stop_loss_pct)

            if position_size > self.account.capital * 0.1:
                position_size = self.account.capital * 0.1

            self.account.position = position_size
            self.account.entry_price = current_price
            self.account.stop_loss = stop_loss

        elif action == 'sell':
            # 类似处理空头逻辑
            pass

    def close_position(self):
        """平仓操作"""
        if self.account.position == 0:
            return

        # 计算平仓收益
        current_price = self.hour_chan[0][-1].lst[-1].close
        profit = (current_price - self.account.entry_price) * self.account.position
        self.account.capital += profit

        # 更新交易记录
        self.account.trade_history.append({
            'type': 'sell' if self.account.position > 0 else 'buy',
            'price': current_price,
            'value': self.account.capital,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # 重置持仓状态
        self.account.position = 0
        self.account.entry_price = 0
        self.account.stop_loss = 0

    def manage_position(self):
        current_price = self.hour_chan[0][-1].lst[-1].close

        # 动态止损
        if self.account.position > 0:
            if current_price <= self.account.stop_loss:
                self.close_position()
            else:
                # 移动止损
                new_stop = max(self.account.stop_loss,
                               current_price - 2 * self.atr)
                self.account.stop_loss = new_stop

        # 止盈逻辑
        if self.account.entry_price and self.account.entry_price != 0:
            profit_ratio = (current_price - self.account.entry_price) / self.account.entry_price
            if profit_ratio >= 0.02:
                self.account.stop_loss = self.account.entry_price

    def run(self):
        for _ in self.day_chan.step_load():
            self.current_trend = self.detect_trend()

        for _ in self.hour_chan.step_load():
            signal = self.find_third_bs_point()
            if signal:
                self.execute_trade(signal)
            self.manage_position()
            self.account.update_drawdown(self.account.capital)


if __name__ == "__main__":
    config = CChanConfig({
        "trigger_step": True,
        "divergence_rate": 0.6,
        "min_zs_cnt": 1,
        "macd_algo": "peak",
        "bi_algo": "strict",
        "zs_combine_mode": "zs",
        "macd": {"fast": 12, "slow": 26, "signal": 9}
    })

    strategy = EnhancedChanStrategy(config)
    strategy.run()

    print(f"最终净值: {strategy.account.capital:.2f}")
    print(f"最大回撤: {strategy.account.max_drawdown:.2%}")