# 协同过滤 不是很好用
import json
from math import sqrt
import operator
import scipy.sparse as sp
import implicit
import pymysql
from recommend_v1_sql import load_dic, save_dic, print_list
from sql_test import get_book_info, get_user_history

user2idx = {}
idx2user = {}
item2idx = {}
idx2item = {}

# 构建用户-->图书的倒排
def loadData(cur):
    data = {}
    user_idx = 0
    item_idx = 0

    for line in cur.fetchall():
        user_id = line[0]
        item_id = line[1]
        # book_title = get_book_info(item_id)
        # if book_title == "No Title!" or book_title == "馆际互借代借国家图书馆图书":
        #    continue
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
    print("----建立书籍：用户的倒排----")
    # print(data)
    return data

# 获取推荐书籍列表
def get_recommend_book(book_id_list):
    book_title_list = []
    for book_id in book_id_list:
        book_id = idx2item[book_id[0]]
        book_title = get_book_info(book_id)
        book_title_list.append(book_title)
        # print(book_title)
    return book_title_list

if __name__ == "__main__":
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    password = "284284dfl" # 密码
    database =  "loan" # 数据库名称
    db = pymysql.connect(host=server, user=user, passwd=password, db=database)
    cur = db.cursor()
    # sql = cur.execute("show tables;")
    # cur.execute("SELECT altid, item_id, ckey FROM userlog LIMIT 2600000") #共7974414条记录
    cur.execute("SELECT altid, item_id, ckey FROM userlog") #共7974414条记录
    data = loadData(cur)  # 获得数据

    # initialize a model
    model = implicit.als.AlternatingLeastSquares(factors=10, calculate_training_loss=True, random_state=1)
    # model = implicit.bpr.BayesianPersonalizedRanking(factors=5)
    model.fit(data)

    user_id = "00639061"
    user_items = data.T.tocsr()
    recommend_book_id_list = model.recommend(user2idx[user_id], user_items)
    history_book_title_list = get_user_history(user_id)
    recommend_book_title_list = get_recommend_book(recommend_book_id_list)
    print("借书历史：")
    print_list(history_book_title_list)
    print(len(history_book_title_list))
    print()
    print("推荐书单：")
    print_list(recommend_book_title_list)