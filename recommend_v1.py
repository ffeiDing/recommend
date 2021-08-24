import openpyxl
import json
from math import sqrt
import operator
import pymysql

workbook = openpyxl.load_workbook("data/loan.xlsx")
shenames = workbook.sheetnames
# print(shenames)

worksheet = workbook["checkedin"]
# print(worksheet) 


# 1.构建用户-->图书的倒排
def loadData(sheet):
    data = {}
    for row in sheet.rows:
        jsonb = json.loads(row[1].value)
        # print(jsonb)
        if "userId" in jsonb and "itemId" in jsonb:
            user_id = jsonb["userId"]
            book_id = jsonb["itemId"]
            data.setdefault(user_id,{})
            data[user_id][book_id] = 1
    print("----1.用户：书籍的倒排----")
    # print(data)
    return data

# 2.1 构造图书-->图书的共现矩阵
# 2.2 计算图书与图书的相似矩阵
def similarity(data):
    # 2.1 构造图书：图书的共现矩阵
    N = {}  # 借阅图书i的总人数
    C = {}  # 借阅图书i也借阅图书j的人数
    for user, item_score_pairs in data.items():
        for item_i, score in item_score_pairs.items():
            N.setdefault(item_i, 0)
            N[item_i] += 1
            C.setdefault(item_i, {})
            for item_j, score in item_score_pairs.items():
                if item_j != item_i:
                    C[item_i].setdefault(item_j, 0)
                    C[item_i][item_j] += 1

    print("---2.构造的共现矩阵---")
    # print('N:', N)
    # print('C', C)

    # 2.2 计算图书与图书的相似矩阵
    W = {}
    for item_i, other_items in C.items():
        W.setdefault(item_i, {})
        for item_j, cnt in other_items.items():
            W[item_i].setdefault(item_j, 0)
            W[item_i][item_j] = C[item_i][item_j] / sqrt(N[item_i]* N[item_j])
    print("---3.构造的相似矩阵---")
    # print(W)
    return W

# 3.根据用户的历史记录，给用户推荐图书
def recommandList(data, W, user, k=3, N=10):
    rank = {}
    for item_i, item_i_score in data[user].items():  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        print(item_i)
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in data[user].keys():  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                rank[item_j] += float(item_i_score) * sim_value

    print("---4.为某个用户推荐----")
    return sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]

data = loadData(worksheet)  # 获得数据
W = similarity(data)  # 计算图书相似矩阵
print(recommandList(data, W, "4a7c1ceb-0e26-4a24-ad4f-f782587cb49f", 10, 10))  #推荐