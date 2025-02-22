from datetime import datetime

from ChanConfig import CChanConfig
from Common.CEnum import KL_TYPE


class TradingPosition:
    def __init__(self, entry_price, position_size, entry_type, entry_time, pattern_type):
        self.entry_price = entry_price
        self.position_size = position_size
        self.entry_type = entry_type  # 'long' 或 'short'
        self.entry_time = entry_time
        self.pattern_type = pattern_type  # 记录入场时的分型类型
        self.exit_pattern = None  # 记录需要等待的出场分型


class EnhancedChanStrategy:
    def __init__(self, config):
        # 原有初始化代码...
        self.positions = []  # 记录所有持仓
        self.pattern_conditions = {
            'first_buy': self.check_first_buy_point,
            'second_buy': self.check_second_buy_point,
            'third_buy': self.check_third_buy_point,
            'first_sell': self.check_first_sell_point,
            'second_sell': self.check_second_sell_point,
            'third_sell': self.check_third_sell_point
        }

    def check_first_buy_point(self, kline_list):
        """第一类买点判断"""
        try:
            if len(kline_list.bi_list) < 3:
                return None

            last_bi = kline_list.bi_list[-1]
            prev_bi = kline_list.bi_list[-2]

            # 向下笔新低后出现的第一个向上笔
            if (not prev_bi.is_up and last_bi.is_up and
                    last_bi.low > prev_bi.low):
                return ('buy', 'first', prev_bi.low)
        except Exception as e:
            print(f"第一类买点判断错误: {str(e)}")
        return None

    def check_second_buy_point(self, kline_list):
        """第二类买点判断"""
        try:
            if len(kline_list.bi_list) < 5:
                return None

            last_bi = kline_list.bi_list[-1]
            zs_list = kline_list.zs_list[-2:]

            if zs_list and last_bi.is_up:
                for zs in zs_list:
                    if last_bi.high > zs.high:  # 突破中枢上沿
                        return ('buy', 'second', zs.low)
        except Exception as e:
            print(f"第二类买点判断错误: {str(e)}")
        return None

    def check_third_buy_point(self, kline_list):
        """第三类买点判断"""
        try:
            if not kline_list.zs_list:
                return None

            last_zs = kline_list.zs_list[-1]
            current_price = kline_list[-1].lst[-1].close
            macd_data = self.get_macd_data(self.hour_chan)

            if (current_price > last_zs.high and
                    macd_data['hist'][-1] > macd_data['hist'][-3] and
                    macd_data['dif'][-1] > macd_data['dea'][-1]):
                return ('buy', 'third', last_zs.high)
        except Exception as e:
            print(f"第三类买点判断错误: {str(e)}")
        return None

    def check_sell_points(self):
        """检查所有卖点"""
        results = []
        for check_func in [self.check_first_sell_point,
                           self.check_second_sell_point,
                           self.check_third_sell_point]:
            result = check_func(self.hour_chan[KL_TYPE.K_60M])
            if result:
                results.append(result)
        return results

    def check_exit_patterns(self):
        """检查是否出现出场分型"""
        try:
            hour_kl_list = self.hour_chan[KL_TYPE.K_60M]
            if len(hour_kl_list.fx_list) < 3:
                return

            current_fx = hour_kl_list.fx_list[-1]

            for position in self.positions[:]:  # 使用切片创建副本进行迭代
                if position.entry_type == 'long':
                    # 多头寻找顶分型
                    if current_fx.type == 'top':
                        self.close_specific_position(position, '顶分型出场')
                elif position.entry_type == 'short':
                    # 空头寻找底分型
                    if current_fx.type == 'bottom':
                        self.close_specific_position(position, '底分型出场')

        except Exception as e:
            print(f"出场分型检查错误: {str(e)}")

    def execute_trade(self, signal):
        """执行交易"""
        if not signal or not self.account.check_risk():
            return

        try:
            action, pattern_type, pivot = signal
            current_price = self.hour_chan[0][-1].lst[-1].close

            # 计算仓位大小
            position_size = self.calculate_position_size(current_price, pivot)

            if action == 'buy':
                # 开多仓
                new_position = TradingPosition(
                    entry_price=current_price,
                    position_size=position_size,
                    entry_type='long',
                    entry_time=datetime.now(),
                    pattern_type=pattern_type
                )
                self.positions.append(new_position)
                self.account.add_trade_record('buy', current_price, position_size, f"{pattern_type}类买点入场")

            elif action == 'sell':
                # 开空仓
                new_position = TradingPosition(
                    entry_price=current_price,
                    position_size=position_size,
                    entry_type='short',
                    entry_time=datetime.now(),
                    pattern_type=pattern_type
                )
                self.positions.append(new_position)
                self.account.add_trade_record('sell', current_price, position_size, f"{pattern_type}类卖点入场")

        except Exception as e:
            print(f"交易执行错误: {str(e)}")

    def close_specific_position(self, position, reason):
        """平掉特定持仓"""
        try:
            current_price = self.hour_chan[0][-1].lst[-1].close

            if position.entry_type == 'long':
                profit = (current_price - position.entry_price) * position.position_size
            else:  # short
                profit = (position.entry_price - current_price) * position.position_size

            self.account.capital += profit
            self.account.add_trade_record(
                'close',
                current_price,
                position.position_size,
                f"{reason} - 从{position.entry_price}到{current_price}"
            )

            self.positions.remove(position)

        except Exception as e:
            print(f"平仓操作错误: {str(e)}")

    def run(self):
        """策略运行主循环"""
        try:
            for _ in self.day_chan.step_load():
                self.current_trend = self.detect_trend()

            for _ in self.hour_chan.step_load():
                # 检查所有可能的买卖点
                buy_signals = []
                for pattern_name, check_func in self.pattern_conditions.items():
                    if pattern_name.startswith('buy'):
                        signal = check_func(self.hour_chan[KL_TYPE.K_60M])
                        if signal:
                            buy_signals.append(signal)

                sell_signals = self.check_sell_points()

                # 执行交易信号
                for signal in buy_signals + sell_signals:
                    self.execute_trade(signal)

                # 检查出场分型
                self.check_exit_patterns()

                # 更新账户状态
                self.account.update_drawdown(self.hour_chan[0][-1].lst[-1].close)

        except Exception as e:
            print(f"策略运行错误: {str(e)}")


if __name__ == "__main__":
    config = CChanConfig({
        "trigger_step": True,
        "divergence_rate": 0.6,
        "min_zs_cnt": 1,
        "bs_type": "3a",
        "macd_algo": "peak",
        "bi_algo": "strict",
        "zs_combine_mode": "zs",
        "macd": {"fast": 12, "slow": 26, "signal": 9}
    })

    strategy = EnhancedChanStrategy(config)
    strategy.run()
