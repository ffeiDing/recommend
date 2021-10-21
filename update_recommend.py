# 借书历史根据时间加权
# 更新 目前信息20210903

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

def update_data(cur, data, N, S, W):
    # cur.execute("SELECT altid, item_id, ckey FROM userlog ORDER BY date_checkout DESC LIMIT 5000000") #共7974414条记录
    cur.execute("SELECT altid, item_id, ckey FROM userlog") #共7974414条记录
    # print(cur.fetchone())
    data = {}

    for line in cur.fetchall():
        user_id = line[0]
        book_id = line[1]
        book_ckey = line[2]
        data.setdefault(user_id,{}) 
        if user_id not in data.keys():
            data.setdefault(user_id,{})
        if book_ckey not in data[user_id].keys():
            if book_ckey not in N.keys():
                N.setdefault(book_ckey, 0)
                S.setdefault(book_ckey, {})
                W.setdefault(book_ckey, {})
            N[book_ckey] += 1
            for other_book in data[user_id].keys():
                S[book_ckey].setdefault(other_book, 0)
                S[book_ckey][other_book] += 1
                S[other_book].setdefault(book_ckey, 0)
                S[other_book][book_ckey] += 1
                W[book_ckey][other_book] = S[book_ckey][other_book] / sqrt(N[book_ckey]* N[other_book])
                W[other_book][book_ckey] = W[book_ckey][other_book]
            data[user_id][book_ckey] = 1

    # print(data)
    save_dic("data/data_20211018update.pkl", data)
    save_dic("data/S_20211018update.pkl", S)
    save_dic("data/W_20211018update.pkl", W)
    save_dic("data/N_20211018update.pkl", N)
    return data, W


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
                # rank[item_j] += float(item_i_score) * sim_value
                rank[item_j] += float(item_i_score) * sim_value * idx * book_weight
                # rank[item_j] += float(item_i_score) * sim_value * (idx * book_weight + 1)
        idx += 1

    print("----4.为某个用户推荐----")
    recommend_ckey_list = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]
    return recommend_ckey_list, get_book_title_list_by_ckey_list(recommend_ckey_list)



# 3.根据用户的历史记录，给用户推荐图书
def recommend_by_all_user(data, W, k=3, N=10):
    recommend = {}
    user_idx = 0
    reader = load_dic("data/reader_info.pkl")
    for user in data.keys():
        if user not in reader.keys():
            continue
        user_idx += 1
        rank = {}
        book_weight = 1.0/len(data[user])
        idx = 1
        for item_i, item_i_score in data[user].items():  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
            # print(item_i)
            for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
                if item_j not in data[user].keys():  # 该相似的图书不在用户user的记录里
                    rank.setdefault(item_j, 0)
                    rank[item_j] += float(item_i_score) * sim_value
                    # rank[item_j] += float(item_i_score) * sim_value * idx * book_weight
                    # rank[item_j] += float(item_i_score) * sim_value * (idx * book_weight + 1)
            idx += 1

        print("----为用户"+str(user_idx)+"推荐----")
        recommend_ckey_list = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]
        recommend_book_title_list = get_book_title_list_by_ckey_list(recommend_ckey_list)
        recommend.setdefault(user, {})
        recommend[user]["ckey_list"] = recommend_ckey_list
        recommend[user]["title_list"] = recommend_book_title_list
    save_dic("data/recommend_20211019update.pkl", recommend)
    return


def recommend_by_history_book_ckey_list(history_list, W, k=3, N=10):
    rank = {}
    book_weight = 1.0/len(history_list)
    idx = 1
    for item_i in history_list:  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        item_i_score = 1.0
        item_same_type = 1.0
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in history_list:  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                # rank[item_j] += float(item_i_score) * sim_value
                if item_j[0] == item_i[0]:
                    item_same_type = 10
                    print(item_i)
                    print(item_j)
                    print(item_same_type)
                else:
                    item_same_type = 1
                rank[item_j] += float(item_i_score) * sim_value * idx * book_weight * item_same_type
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
    test = True
    if test:
        recommend = load_dic("data/recommend_20211020_all.pkl")
        print(recommend["1906194055"])
    else:
        server = "127.0.0.1"    # 数据库服务器名称或IP
        user = "root"   #  用户名
        password = "284284dfl" # 密码
        database =  "loan_new" # 数据库名称
        data = load_dic("data/data_20211018update.pkl")
        W = load_dic("data/W_20211018update.pkl")
        # N = load_dic("data/N_20211018update.pkl")
        # S = load_dic("data/S_20211018update.pkl")

        # # data = {}
        # # W = {}
        # # N = {}
        # # S = {}
        # db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        # cur = db.cursor()
        # data, W = update_data(cur, data, N, S, W)
        recommend_by_all_user(data, W, 10, 50)

        # user_id = "0006182129" # "1606191027" # "0006171162"
        # # user_file_name = "data/iPatron_1906194055_userlog_1.xlsx" # "data/iPatron_1906194055_userlog_1.xlsx"

        # _, recommend_book_title_list = recommend_by_user_id(data, W, user_id, 10, 40)  #推荐
        # # recommend_book_title_list = recommend_by_user_xls(user_file_name, W, 10, 40)

        # history_book_title_list = get_history_book_title_list_by_user_id(user_id)
        # # history_book_title_list = get_user_history_book_title_list_from_xls(user_file_name)

        # print("借书历史：")
        # print_list(history_book_title_list)
        # print(len(history_book_title_list))
        # print()
        # print("推荐书单：")
        # print_list(recommend_book_title_list)
    
