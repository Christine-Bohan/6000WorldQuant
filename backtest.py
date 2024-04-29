import numpy as np
import pandas as pd
import datetime as dt

# 回测程序
def run_backtest(data,signal, init_cash, commission, multiplier, mintick, begin_date, end_date):
    # 止盈止损
    stop = 0.1
    stopwin = 0.1

    # 记录组合价值
    portfolio_value_ser = pd.Series(init_cash, index=[signal.index[0]])
    # 记录交易详情
    trade_record_df = pd.DataFrame()
    # 记录持仓状态
    status = None
    for i in range(1, len(signal)):
        # 日期
        datetime = signal.index[i]
        pre_datetime = signal.index[i - 1]

        # 如果没有持仓
        if status == None:
            # 如果有做多信号
            if signal.loc[pre_datetime,'signal'] == 1:
                # 计算可买手数
                amount = int(portfolio_value_ser.iloc[-1] / ((data.loc[datetime, 'open'] + mintick) * multiplier))
                # 扣除手续费和滑点
                portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] - (
                            amount * multiplier * data.loc[datetime, 'open'] * commission) - (
                                                            amount * multiplier * mintick)
                # 记录交易详情
                trade_record_df.loc[len(trade_record_df), 'datetime'] = datetime
                trade_record_df.loc[len(trade_record_df) - 1, 'side'] = '做多'
                trade_record_df.loc[len(trade_record_df) - 1, 'amount'] = amount
                trade_record_df.loc[len(trade_record_df) - 1, '价格'] = data.loc[datetime, 'open'] + mintick
                trade_record_df.loc[len(trade_record_df) - 1, '金额'] = (data.loc[
                                                                             datetime, 'open'] + mintick) * amount * multiplier
                trade_record_df.loc[len(trade_record_df) - 1, '盈亏'] = 0
                # 持仓状态
                status = 'long'
            # 如果有空头信号
            elif signal.loc[pre_datetime,'signal'] == -1:
                # 计算可卖手数
                amount = int(portfolio_value_ser.iloc[-1] / ((data.loc[datetime, 'open'] - mintick) * multiplier))
                # 扣除手续费和滑点
                portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] - (
                            amount * multiplier * data.loc[datetime, 'open'] * commission) - (
                                                            amount * multiplier * mintick)
                # 记录交易详情
                trade_record_df.loc[len(trade_record_df), 'datetime'] = datetime
                trade_record_df.loc[len(trade_record_df) - 1, 'side'] = '做空'
                trade_record_df.loc[len(trade_record_df) - 1, 'amount'] = amount
                trade_record_df.loc[len(trade_record_df) - 1, '价格'] = data.loc[datetime, 'open'] - mintick
                trade_record_df.loc[len(trade_record_df) - 1, '金额'] = (data.loc[
                                                                             datetime, 'open'] - mintick) * amount * multiplier
                trade_record_df.loc[len(trade_record_df) - 1, '盈亏'] = 0
                # 持仓状态
                status = 'short'
            # 如果没有多空信号
            else:
                # 当日盈亏
                portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1]

        # 如果有多头持仓
        elif status == 'long':
            # 持仓手数
            amount = trade_record_df[trade_record_df['side'] == '做多']['amount'].values[-1]
            # 买入日的bar位置
            start_bar = trade_record_df[trade_record_df['side'] == '做多']['datetime'].values[-1]
            # 分母
            denominator = data.loc[start_bar:pre_datetime, 'volume'][-200:].sum()
            # 分子
            numerator = np.maximum.accumulate(data.loc[start_bar:pre_datetime, 'low'][-200:]) @ data.loc[
                                                                                                start_bar:pre_datetime,
                                                                                                'volume'][-200:]
            # 监控条件
            if data.loc[pre_datetime, 'low'] <= np.max(numerator / denominator) * (1 - stop):
                # 止损/止盈
                if  data.loc[pre_datetime, 'close'] / data.loc[start_bar, 'close'] - 1 > stopwin:
                    # 扣除手续费和滑点
                    portfolio_value_ser[datetime] = portfolio_value_ser[-1] - (
                                amount * multiplier * data.loc[datetime, 'open'] * commission) - (
                                                                amount * multiplier * mintick)
                    # 记录交易详情
                    trade_record_df.loc[len(trade_record_df), 'datetime'] = datetime
                    trade_record_df.loc[len(trade_record_df) - 1, 'side'] = '平多'
                    trade_record_df.loc[len(trade_record_df) - 1, 'amount'] = -amount
                    trade_record_df.loc[len(trade_record_df) - 1, '价格'] = data.loc[datetime, 'open'] - mintick
                    trade_record_df.loc[len(trade_record_df) - 1, '金额'] = (data.loc[
                                                                                 datetime, 'open'] - mintick) * amount * multiplier
                    trade_record_df.loc[len(trade_record_df) - 1, '盈亏'] = (data.loc[
                                                                                 datetime, 'open'] - mintick) * amount * multiplier - \
                                                                            trade_record_df[
                                                                                trade_record_df['side'] == '做多'][
                                                                                '金额'].values[-1]
                    # 持仓状态
                    status = None
                else:
                    # 当日盈亏
                    portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] + (
                                amount * multiplier * (data.loc[datetime, 'close'] - data.loc[pre_datetime, 'close']))
            else:
                # 当日盈亏
                portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] + (
                            amount * multiplier * (data.loc[datetime, 'close'] - data.loc[pre_datetime, 'close']))
        # 如果有空头持仓
        elif status == 'short':
            # 持仓手数
            amount = trade_record_df[trade_record_df['side'] == '做空']['amount'].values[-1]
            # 买入日的bar位置
            start_bar = trade_record_df[trade_record_df['side'] == '做空']['datetime'].values[-1]
            # 分母
            denominator = data.loc[start_bar:pre_datetime, 'volume'][-200:].sum()
            # 分子
            numerator = np.minimum.accumulate(data.loc[start_bar:pre_datetime, 'high'][-200:]) @ data.loc[
                                                                                                 start_bar:pre_datetime,
                                                                                                 'volume'][-200:]
            # 监控条件
            if data.loc[pre_datetime, 'high'] >= np.min(numerator / denominator) * (1 + stop):
                # 止损/止盈
                if  data.loc[pre_datetime, 'close'] / data.loc[start_bar, 'close'] - 1 < -stopwin:
                    # 扣除手续费和滑点
                    portfolio_value_ser[datetime] = portfolio_value_ser[-1] - (
                                amount * multiplier * data.loc[datetime, 'open'] * commission) - (
                                                                amount * multiplier * mintick)
                    # 记录交易详情
                    trade_record_df.loc[len(trade_record_df), 'datetime'] = datetime
                    trade_record_df.loc[len(trade_record_df) - 1, 'side'] = '平空'
                    trade_record_df.loc[len(trade_record_df) - 1, 'amount'] = -amount
                    trade_record_df.loc[len(trade_record_df) - 1, '价格'] = data.loc[datetime, 'open'] + mintick
                    trade_record_df.loc[len(trade_record_df) - 1, '金额'] = (data.loc[
                                                                                 datetime, 'open'] + mintick) * amount * multiplier
                    trade_record_df.loc[len(trade_record_df) - 1, '盈亏'] = -(
                                data.loc[datetime, 'OPEN'] + mintick) * amount * multiplier + trade_record_df[
                                                                                trade_record_df['side'] == '做空'][
                                                                                '金额'].values[-1]
                    # 持仓状态
                    status = None
                else:
                    # 当日盈亏
                    portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] - (
                                amount * multiplier * (data.loc[datetime, 'close'] - data.loc[pre_datetime, 'close']))
            else:
                # 当日盈亏
                portfolio_value_ser[datetime] = portfolio_value_ser.iloc[-1] - (
                            amount * multiplier * (data.loc[datetime, 'close'] - data.loc[pre_datetime, 'close']))

    return portfolio_value_ser, trade_record_df


# 获取回测结果相关信息
def get_backtest_info(portfolio_value_ser):
    # 5分钟数据转为日线数据
    # portfolio_value_ser = portfolio_value_ser.resample('1D').last().dropna()
    # 计算组合收益率和累计收益率
    ret_ser = portfolio_value_ser.pct_change().dropna()
    cum_ret_ser = (portfolio_value_ser.pct_change().fillna(0) + 1).cumprod()

    # 评价指标
    result = pd.Series(dtype='float64')
    result['年化收益率'] = cum_ret_ser.iloc[-1] ** (252 / len(cum_ret_ser)) - 1
    result['年化波动率'] = ret_ser.std() * np.sqrt(252)
    result['最大回撤'] = max((np.maximum.accumulate(cum_ret_ser) - cum_ret_ser) / np.maximum.accumulate(cum_ret_ser))
    result['夏普比率'] = (result['年化收益率']) / result['年化波动率']
    result['Calmar'] = (result['年化收益率']) / result['最大回撤']

    # 改为百分比格式
    result['年化收益率'] = '%.2f%%' % (result['年化收益率'] * 100)
    result['年化波动率'] = '%.2f%%' % (result['年化波动率'] * 100)
    result['最大回撤'] = '%.2f%%' % (result['最大回撤'] * 100)
    result['夏普比率'] = '%.2f' % (result['夏普比率'])
    result['Calmar'] = '%.2f' % (result['Calmar'])

    return result