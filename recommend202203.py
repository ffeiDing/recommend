# 借书历史根据时间加权

# 同一大类图书加权(已取消)

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
def loadData(cur_list):
    data = {}
    callnum2ckey = load_dic("data/callnum2ckey.pkl")
    for cur in cur_list:
    # cur.execute("SELECT altid, item_id, ckey FROM userlog ORDER BY date_checkout DESC LIMIT 5000000") #共7974414条记录
        cur.execute("SELECT altid, callno FROM userlog") # 9213235 178874名用户
        # print(cur.fetchall()[0][0])
        sql_line = 0
        for line in cur.fetchall():
            user_id = line[0]
            book_callnum = line[1]
            if book_callnum not in callnum2ckey.keys():
                # print(book_callnum)
                continue
            book_ckey = callnum2ckey[book_callnum]
            data.setdefault(user_id,{})
            data[user_id][book_ckey] = 1
            sql_line += 1
        print("----1.建立用户：书籍的倒排----")
        print(sql_line)                              
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
    return recommend_ckey_list



# 3.根据用户的历史记录，给用户推荐图书
def recommend_by_all_user(data, W, k=3, N=10):
    recommend = {}
    user_idx = 0
    # reader = load_dic("data/reader_info.pkl")
    for user in data.keys():
        # if user not in reader.keys():
        #     continue
        user_idx += 1
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

        print("----为用户"+str(user_idx)+"推荐----")
        recommend_ckey_list = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]
        recommend.setdefault(user, {})
        recommend[user]["ckey_list"] = recommend_ckey_list
        # recommend[user]["title_list"] = recommend_book_title_list
    save_dic("data/recommend_202203.pkl", recommend)
    return


def recommend_by_history_book_ckey_list(history_list, W, k=3, N=10):
    rank = {}
    book_weight = 1.0/len(history_list)
    idx = 1
    for item_i in history_list:  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        item_i_score = 1.0
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in history_list:  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                rank[item_j] += float(item_i_score) * sim_value * idx * book_weight
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
    load_data = False # 是否读取保存的数据
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    month_list = ["202110", "202111", "202112", "202201", "202202", "202203"]
    password = "284284dfl" # 密码
    database =  "userlog_20211020" # 数据库名称
    if load_data:
        data = load_dic("data/data_202203.pkl")
        W = load_dic("data/W_202203.pkl")
    else:
        cur_list = []
        db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        cur_list.append(db.cursor())
        for i in month_list:
            database_month = "userlog_" + i
            db_month = pymysql.connect(host=server, user=user, passwd=password, db=database_month)
            cur_list.append(db_month.cursor())
        data = loadData(cur_list)  # 获得数据
        save_dic("data/data_202203.pkl", data)
        W = similarity(data)  # 计算图书相似矩阵
        save_dic("data/W_202203.pkl", W)
        print("---已保存数据---")
    
    recommend_by_all_user(data, W, 10, 200)

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
    
