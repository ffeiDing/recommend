# 使用书籍的ckey代替id  没有时间加权

from math import sqrt
import operator
import pymysql
import pickle
from sql_test import *

def save_dic(name, dic):
    with open(name, 'wb') as f:
        pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)

def load_dic(name):
    with open(name, 'rb') as f:
        return pickle.load(f)       


# 1.构建用户-->图书的倒排
def loadData(cur):
    # cur.execute("SELECT altid, item_id, ckey FROM userlog ORDER BY date_checkout DESC LIMIT 5000000") #共7974414条记录
    cur.execute("SELECT altid, item_id, ckey FROM userlog") #共7974414条记录
    # print(cur.fetchone())
    data = {}

    for line in cur.fetchall():
        user_id = line[0]
        book_id = line[1]
        book_ckey = line[2]
        data.setdefault(user_id,{})
        data[user_id][book_ckey] = 1
    print("----1.建立用户：书籍的倒排----")
    # print(data)
    return data

# 2.1 构造图书-->图书的共现矩阵
# 2.2 计算图书与图书的相似矩阵
def similarity(data):
    # 2.1 构造图书：图书的共现矩阵
    N = {}  # 借阅图书i的总人数
    W = {}  # 借阅图书i也借阅图书j的人数
    for user, item_score_pairs in data.items():
        for item_i, score in item_score_pairs.items():
            N.setdefault(item_i, 0)
            N[item_i] += 1
            W.setdefault(item_i, {})
            for item_j, score in item_score_pairs.items():
                if item_j != item_i:
                    W[item_i].setdefault(item_j, 0)
                    W[item_i][item_j] += 1

    print("----2.构造共现矩阵----")
    # print('N:', N)
    # print('C', C)

    # 2.2 计算图书与图书的相似矩阵
    # W = {}
    for item_i, other_items in W.items():
        W.setdefault(item_i, {})
        for item_j, cnt in other_items.items():
            # W[item_i].setdefault(item_j, 0)
            W[item_i][item_j] = W[item_i][item_j] / sqrt(N[item_i]* N[item_j])
    print("----3.构造相似矩阵----")
    # print(W)
    return W

# 3.根据用户的历史记录，给用户推荐图书
def recommend_by_user_id(data, W, user, k=3, N=10):
    rank = {}
    book_weight = 1.0/len(data[user])
    idx = 1
    for item_i, item_i_score in data[user].items():  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        # print(item_i)
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in data[user].keys():  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                rank[item_j] += float(item_i_score) * sim_value * idx * book_weight
                # rank[item_j] += float(item_i_score) * sim_value * (idx * book_weight + 1)
        idx = idx + 1

    print("----4.为某个用户推荐----")
    recommend_ckey_list = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]
    return get_book_title_list_by_ckey_list(recommend_ckey_list)


def recommend_by_history_book_ckey_list(history_list, W, k=3, N=10):
    rank = {}
    book_weight = 1.0/len(history_list)
    idx = 1
    for item_i in history_list:  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        item_i_score = 1.0
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in history_list:  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                rank[item_j] += float(item_i_score) * sim_value 
                # rank[item_j] += float(item_i_score) * sim_value * (idx * book_weight + 1)
        idx = idx + 1
    print("----4.为某个用户推荐----")
    recommend_ckey_list = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]
    return get_book_title_list_by_ckey_list(recommend_ckey_list)


def recommend_by_user_xls(file_name, W, k=3, N=10):
    book_id_list = get_user_history_book_id_list_from_xls(file_name)
    book_ckey_list = get_ckey_list_by_book_id_list(book_id_list)
    recommend_title_list = recommend_by_history_book_ckey_list(book_ckey_list, W, k, N)
    return recommend_title_list


def print_list(list_name):
    for i in list_name:
        print(i)


if __name__ == "__main__":
    load_data = True # 是否读取保存的数据
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    password = "284284dfl" # 密码
    database =  "loan" # 数据库名称
    if load_data:
        data = load_dic("data/data_v1.2.pkl")
        W = load_dic("data/W_v1.2.pkl")
    else:
        db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        cur = db.cursor()
        data = loadData(cur)  # 获得数据
        save_dic("data/data_v1.2.pkl", data)
        W = similarity(data)  # 计算图书相似矩阵
        save_dic("data/W_v1.2.pkl", W)
        print("---已保存数据---")

    # user_id = "1606191027" # "1606191027" # "0006171162"
    user_file_name = "data/iPatron_1906194055_userlog.xlsx"

    # recommend_book_title_list = recommend_by_user_id(data, W, user_id, 10, 40)  #推荐
    recommend_book_title_list = recommend_by_user_xls(user_file_name, W, 10, 40)

    # history_book_title_list = get_history_book_title_list_by_user_id(user_id)
    history_book_title_list = get_user_history_book_title_list_from_xls(user_file_name)
    print("借书历史：")
    print_list(history_book_title_list)
    print(len(history_book_title_list))
    print()
    print("推荐书单：")
    print_list(recommend_book_title_list)
