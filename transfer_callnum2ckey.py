# 先清洗数据，仅留下jsonb的action为checkedout的条目
import csv
from os import RTLD_NOW
import pickle


callnum2ckey = {}
with open("data/SIRSI_CALLNUM.csv") as csvfile:
    reader = csv.reader((line.replace('\0','') for line in csvfile)) 
    for row in reader:  
        callnum2ckey[row[3]] = row[0]

def save_dic(name, dic):
    with open(name, 'wb') as f:
        pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)

# print(callnum2ckey)

save_dic("data/callnum2ckey.pkl", callnum2ckey)
