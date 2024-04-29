import pandas as pd
from backtest import run_backtest,get_backtest_info
import matplotlib.pyplot as plt

merged_data = pd.read_csv('./data/merged_data.csv')
merged_data['Date'] = pd.to_datetime(merged_data['date'])  # 将字符串列转换为datetime对象
merged_data.set_index('Date', inplace=True)  # 将date列设置为索引

#print(merged_data)
#print(type(merged_data.loc[0,'date']))
signal = merged_data[['signal']]
signal.index = signal.index + pd.DateOffset(hours=0, minutes=0, seconds=0)
# pre_datetime = signal.index[3]
# print(merged_data.loc[pre_datetime, 'open'])
# print(signal.loc[pre_datetime,:])
# print(pre_datetime)
# print(type(pre_datetime))
# # print(signal.index)

data=merged_data
signal=signal
init_cash=1000000
commission=0.0001
multiplier=1
mintick=0.001
#print(merged_data['date'].iloc[0])
begin_date=merged_data['date'].iloc[1]
end_date=merged_data['date'].iloc[-1]

# 回测
# 记录组合价值
total_portfolio_value_ser = pd.DataFrame()
# 记录所有交易记录
all_trade_record_df = pd.DataFrame()
portfolio_value_ser, trade_record_df = run_backtest(data,signal, init_cash, commission, multiplier, mintick, begin_date, end_date)
# 记录组合价值
total_portfolio_value_ser = pd.concat([total_portfolio_value_ser, portfolio_value_ser], axis=1)
# 记录所有交易记录
all_trade_record_df = pd.concat([all_trade_record_df, trade_record_df], axis=0)
total_portfolio_value_ser.fillna(method='backfill', inplace=True)
total_portfolio_value_ser2 = total_portfolio_value_ser.sum(axis=1)
all_trade_record_df.sort_values('datetime', ascending=True, inplace=True)
all_trade_record_df.index = range(0, len(all_trade_record_df))

# 获取回测结果相关信息
print(get_backtest_info(total_portfolio_value_ser2))
# 作图
plt.plot(total_portfolio_value_ser2.index,total_portfolio_value_ser2)
plt.title('backtesting')
plt.show()


