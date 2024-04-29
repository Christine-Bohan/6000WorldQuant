import pandas as pd
from datetime import datetime

data = pd.read_csv('./data/data.csv')
# data = data.drop(9365)
# print(type(data.loc[0,'body']))
# #str
# print(type(data.loc[0,'publish_time']))
# #str
#print(data.loc[0:5,'publish_time'])

#处理publish_time，创建新列为formatted_time
def format_publish_time(time_str):
    try:
        datetime_str = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S%z")
    except:
        return 0
    #return datetime_str.strftime("%Y-%m-%d %H:%M")
    return datetime_str.strftime("%Y-%m-%d")

data['formatted_time'] = data['publish_time'].apply(format_publish_time)

# 删除字符串时间不符的行
new_data = data.drop(data[data['formatted_time'] == 0].index)

# print(data.shape) #22025
# print(new_data.shape) #22017

# 将字符串列转换为datetime对象
new_data['formatted_time'] = pd.to_datetime(new_data['formatted_time'])

# 将formatted_time列设置为索引
new_data.set_index('formatted_time', inplace=True)

# 按时间排序DataFrame
new_data.sort_index(inplace=True)

#只保留body列
new_data = new_data[['body']]

#删除dataframe的index相同的行
duplicate_rows = new_data.index.duplicated()
new_data = new_data[~duplicate_rows]

#print(new_data) #12442 rows

new_data.to_csv('./data/new_data.csv')
print(new_data)

# new_data_small = new_data.iloc[15,:]
# new_data_small.to_csv('./data/new_data_small.csv')
# print(new_data_small['body'])


