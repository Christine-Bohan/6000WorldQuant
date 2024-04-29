import yfinance as yf
import matplotlib.dates as mdates
import datetime

# 获取指定股票的行情数据
price = yf.download('^GSPC', start='2022-12-01', end='2023-11-30', interval='1d',auto_adjust=True)

price.to_csv('./data/price.csv')
print(price)