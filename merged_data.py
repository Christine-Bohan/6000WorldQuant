import pandas as pd
from datetime import datetime, timedelta

price = pd.read_csv('./data/price.csv')
signal = pd.read_csv('./data/signal.csv')

#signal日期推后一天
signal['formatted_time'] = pd.to_datetime(signal['formatted_time'])
signal['formatted_time']= signal['formatted_time'] + timedelta(days=1)

# print(price)
# print(signal)

# 合并两个DataFrame，按照日期列进行合并
price['Date'] = pd.to_datetime(price['Date'])
merged_data = pd.merge(price, signal, left_on='Date', right_on='formatted_time')

# 删除多余的formatted_date列
merged_data.drop('formatted_time', axis=1, inplace=True)

merged_data = merged_data[['Date','Open','Close','signal','High','Low','Volume']]
merged_data.rename(columns=lambda x: x[0].lower() + x[1:], inplace=True)

merged_data['date'] = pd.to_datetime(merged_data['date'])  # 将字符串列转换为datetime对象
merged_data.set_index('date', inplace=True)  # 将date列设置为索引

#print(type(merged_data.loc[0,'date']))
print((merged_data))

merged_data.to_csv('./data/merged_data.csv')
