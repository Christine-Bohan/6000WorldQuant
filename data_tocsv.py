import pickle
import pandas as pd
# 从文件中加载 DatasetDict 对象
with open("dataset.pkl", "rb") as f:
    dataset = pickle.load(f)

data_raw = pd.DataFrame(dataset)
data = pd.json_normalize(data_raw['train'])

data.to_csv('./data/data.csv')
print(data)
