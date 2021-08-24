# 协同过滤 不是很好用

import openpyxl
import json
from math import sqrt
import operator
import scipy.sparse as sp
import implicit

workbook = openpyxl.load_workbook("data/loan.xlsx")
shenames = workbook.sheetnames
# print(shenames)

worksheet = workbook["checkedin"]
# print(worksheet) 

user2idx = {}
idx2user = {}
item2idx = {}
idx2item = {}

# 构建用户-->图书的倒排
def loadData(sheet):
    data = {}
    user_idx = 0
    item_idx = 0
    for row in sheet.rows:
        jsonb = json.loads(row[1].value)
        # print(jsonb)
        if "userId" in jsonb and "itemId" in jsonb:
            user_id = jsonb["userId"]
            item_id = jsonb["itemId"]

            if user_id not in user2idx.keys():
                user2idx[user_id] = user_idx
                idx2user[user_idx] = user_id
                user_idx = user_idx + 1
            if item_id not in item2idx.keys():
                item2idx[item_id] = item_idx
                idx2item[item_idx] = item_id
                item_idx = item_idx + 1

            tmp_user_idx = user2idx[user_id]
            tmp_item_idx = item2idx[item_id]

            data.setdefault(tmp_item_idx, [])
            data[tmp_item_idx].append(tmp_user_idx)
        
    row_ind = [k for k, v in data.items() for _ in range(len(v))]
    col_ind = [i for ids in data.values() for i in ids]
    data = sp.csr_matrix(([1]*len(row_ind), (row_ind, col_ind)))
    print("----1.书籍：用户的倒排----")
    # print(data)
    return data

data = loadData(worksheet)  # 获得数据

# initialize a model
model = implicit.als.AlternatingLeastSquares(factors=5, calculate_training_loss=True, random_state=1)
# model = implicit.bpr.BayesianPersonalizedRanking(factors=5)
model.fit(data)

user_items = data.T.tocsr()
recommendations = model.recommend(user2idx["4a7c1ceb-0e26-4a24-ad4f-f782587cb49f"], user_items)
print(recommendations)
for i in range(len(recommendations)):
    print(idx2item[recommendations[i][0]])

# print(recommandList(data, W, "4a7c1ceb-0e26-4a24-ad4f-f782587cb49f", 10, 10))  #推荐