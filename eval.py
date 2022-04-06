# 借书历史根据时间加权

# 同一大类图书加权(已取消)

from math import sqrt
import operator
import pymysql
import pickle
from sql_test import *
import csv

hit_data = {}

def save_dic(name, dic):
    with open(name, 'wb') as f:
        pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)

def load_dic(name):
    with open(name, 'rb') as f:
        return pickle.load(f)       

def eval(recommend_data, loan_list):
    callnum2ckey = load_dic("data/callnum2ckey.pkl")
    for cur in loan_list:
        cur.execute("SELECT altid, callno FROM userlog") 
        for line in cur.fetchall():
            user_id = line[0]
            if user_id not in recommend_data.keys():
                continue
            hit_data.setdefault(user_id,{})
            book_callnum = line[1]
            if book_callnum not in callnum2ckey.keys():
                # print(book_callnum)
                continue
            book_ckey = callnum2ckey[book_callnum]
            if book_ckey in recommend_data[user_id].keys():
                hit_data[user_id][book_ckey] = 1
    # print(hit_data)
    for user_id in hit_data.keys():
        if hit_data[user_id]:
            print(user_id, hit_data[user_id])
    return


if __name__ == "__main__":
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    recommend_month_list = ["202110"]
    loan_month_list = ["202111"]
    password = "284284dfl" # 密码
    recommend_data = {}
    loan_list = []
    for i in recommend_month_list:
        recommend_month = "data/recommend_" + i + ".csv"
        csv_reader = csv.reader(open(recommend_month))
        for line in csv_reader:
            # print(line[1])
            user_id = line[0]
            recommend_data.setdefault(user_id,{})
            recommend_books = line[1].split(',')
            for book in recommend_books:
                if "'" not in book:
                    continue
                book = book.replace('[', '')
                book = book.replace('(', '')
                book = book.replace('\'', '')
                recommend_data[user_id][book] = 1
                
    for i in loan_month_list:
        database_month = "userlog_" + i
        print(database_month)
        db_month = pymysql.connect(host=server, user=user, passwd=password, db=database_month)
        loan_list.append(db_month.cursor())
    eval(recommend_data, loan_list) 