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
def loadData(cur):
    # cur.execute("SELECT altid, item_id, ckey FROM userlog ORDER BY date_checkout DESC LIMIT 5000000") #共7974414条记录
    cur.execute("SELECT altid, item_id, ckey FROM userlog") #共7974414条记录
    # print(cur.fetchone())
    data = {}

    for line in cur.fetchall():
        user_id = line[0]
        book_id = line[1]
        book_ckey = line[2]
    print(user_id, book_id, book_ckey)
    # print(data)
    return data



if __name__ == "__main__":
    load_data = False # 是否读取保存的数据
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    password = "284284dfl" # 密码
    database =  "loan_new" # 数据库名称
    if load_data:
        data = load_dic("data/data_new.pkl")
        W = load_dic("data/W_new.pkl")
    else:
        db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        cur = db.cursor()
        data = loadData(cur)  # 获得数据
    
    
