#环境设置
from llama_index.llms.azure_openai import AzureOpenAI
import openai, os
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging
import sys
import pandas as pd
import time

api_key = "ab1eb49e3b604fa8a1e853725c9e4dc6"
azure_endpoint = "https://hkust.azure-api.net"
api_version = '2023-05-15'
llm = AzureOpenAI(
    engine='gpt-35-turbo',
    model='gpt-35-turbo',
    temperature=0.0,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version = api_version
)
# response = llm.complete("The sky is a beautiful blue and")
# print(response)
embed_model = AzureOpenAIEmbedding(
    model='text-embedding-ada-002',
    deployment_name='text-embedding-ada-002',
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)
from llama_index.core import Settings
Settings.llm = llm
Settings.embed_model = embed_model


new_data = pd.read_csv('./data/new_data.csv')
new_data['signal'] = 0

epoch = len(new_data)
new_data = new_data.iloc[:epoch,:]

start_time = time.time()
for i in range(epoch):
    new_data_small = new_data.iloc[i, :]
    new_data_small.to_csv('./data/new_data_small.csv')
    #index
    documents = SimpleDirectoryReader('./query').load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.set_index_id("index")
    index.storage_context.persist('./storage')

######
    #query
    query_text = (
        "As an experienced financial analyst, your final response must be a single number: '-1'， '1'， '0’. You must analyze the sentiment of the financial news provided and determine its impact on the stock mentioned. "
        "Consider various factors such as the nature of the news (e.g., earnings report, product launch, regulatory changes), the significance of the news (e.g., unexpected vs. anticipated), and the potential long-term and short-term impact on the stock price.) "
        "For each factor, assign a weighted score on a scale from -10 to 10, where 10 represents the most positive impact and -10 represents the most negative impact. "
        "The weights should reflect the perceived impact of each factor on the stock, based on the following guidelines: "
        "1. Unexpected positive news or significant negative developments should be given higher absolute values. "
        "2. The source and credibility of the news should influence the weight assigned. "
        "3. Historical performance and context should be considered when determining the weight. "
        "4. No single factor should dominate the score unless it is of critical importance. "
        "Calculate an overall sentiment score by aggregating the weighted scores of each factor. "
        "If the overall sentiment score is positive, indicating potentially good news for the stock, you respond with ‘1’;"
        "if the overall sentiment score is negative, indicating potentially bad news, you respond with '-1';"
        "if you can not make a clear sentiment score, you respond with '0',Your response must be a single number: '1' ,'-1', or '0'. Remember, the goal is to provide a nuanced and informed judgment, not a simple binary response.")
    #query_text = "You must tell me whether or not this is good news for the stock mentioned. You cannot answer you cannot determine. If it is good news, you respond 1; if it is bad news, you respond -1.Notice that you can only respond a single number:1 or -1. "
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    response = str(response)

    if len(response)>2:
        response = 0

    response = int(response)
    # print(type(response))
    new_data.loc[i,'signal'] = response

    if i % 10 == 0 and i>0:
        print(f'当前循环次数为{i}，已运行{time.time()-start_time}秒')


# print(new_data.head(epoch))
# print(sum(new_data['signal']==-1))

signal = new_data[['formatted_time','signal']]
signal.to_csv('./data/signal.csv')
# print(signal.head(epoch))

# #index
# documents = SimpleDirectoryReader('./data').load_data()
# index = VectorStoreIndex.from_documents(documents)
# index.set_index_id("index")
# index.storage_context.persist('./storage')
#
# #query
# query_text = "You must tell me whether or not this is good news for the stock mentioned. You cannot answer you cannot determine. If yes, you respond 1; else you respond 0.Notice that you can only respond a single number:1 or 0"
# query_engine = index.as_query_engine()
# response = query_engine.query(query_text)
# print(response)

# def get_signal(str):
#     #index
#     # 指定保存的文件路径
#     file_path = "./data/file.txt"
#     # 打开文件并写入字符串内容
#     with open(file_path, 'w') as file:
#         file.write(str)
#     print('字符串已保存')
#
#     documents = SimpleDirectoryReader('./data').load_data()
#     index = VectorStoreIndex.from_documents(documents)
#     index.set_index_id("index_luxun")
#     index.storage_context.persist('./storage')
#
#     #query
#     query_engine = index.as_query_engine()
#     response = query_engine.query(
#         "鲁迅的老师叫什么"
#     )
#     print('response')
#
#
#
# new_data_small = pd.read_csv('new_data_small.csv')
# new_data_small['signal'] = new_data_small['body'].apply(get_signal)


