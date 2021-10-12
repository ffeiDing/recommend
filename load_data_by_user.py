# 获取每个读者的借阅列表

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
        data.setdefault(user_id,[])
        data[user_id].append(book_ckey)
    print("----建立用户：书籍的倒排----")
    # print(data)
    return data


def print_list(list_name):
    for i in list_name:
        print(i)


if __name__ == "__main__":
    load_data = True # 是否读取保存的数据
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    password = "284284dfl" # 密码
    database =  "loan_new" # 数据库名称
    if load_data:
        data = load_dic("data/user.pkl")
        print(data)
    else:
        db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        cur = db.cursor()
        data = loadData(cur)  # 获得数据
        save_dic("data/user.pkl", data)
        print("---已保存数据---")