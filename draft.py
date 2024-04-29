import pandas as pd
from datetime import datetime, timedelta

signal = pd.read_csv('./data/signal.csv')
print(signal.head())
signal['formatted_time2'] = pd.to_datetime(signal['formatted_time'])
signal['formatted_time']= signal['formatted_time2'] + timedelta(days=1)
print(signal.head())
print(type(signal['formatted_time'].iloc[0]))