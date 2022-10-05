# 借书历史根据时间加权

# 同一大类图书加权(已取消)

from math import sqrt
import operator
import pymysql
import pickle
from sql_test import *
import csv

def save_dic(name, dic):
    with open(name, 'wb') as f:
        pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)

def load_dic(name):
    with open(name, 'rb') as f:
        return pickle.load(f)       


def get_book_info(book_id):
    if "/" in book_id:
        return "No Title!"
    url = "http://162.105.138.200:8085/symws2016041/rest/standard/lookupTitleInfo?clientID=SymWSTestClient&includeAvailabilityInfo=true&includeOPACInfo=true&includeItemInfo=true&json=true&includeMarcHoldings=true&marcEntryFilter=ALL&titleID="+book_id
    print(url)
    response = requests.get(url)
    # print(response.headers)
    result = response.text
    # print(result)
    book_info = json.loads(result)["TitleInfo"]
    book_title = " "
    if book_info:
        if "title" in book_info[0].keys():
            book_title = book_info[0]["title"]
    # print(book_title)
    return book_title

# 1.构建用户-->图书的倒排
def loadData(cur_list):
    data = {}
    callnum2ckey = load_dic("data/callnum2ckey.pkl")
    for cur in cur_list:
    # cur.execute("SELECT altid, item_id, ckey FROM userlog ORDER BY date_checkout DESC LIMIT 5000000") #共7974414条记录
        cur.execute("SELECT altid, callno FROM userlog") 
    # print(cur.fetchall()[0][0])
        for line in cur.fetchall():
            user_id = line[0]
            book_callnum = line[1]
            if book_callnum not in callnum2ckey.keys():
                print(book_callnum)
                continue
            book_ckey = callnum2ckey[book_callnum]
            data.setdefault(book_ckey, 0)
            data[book_ckey] += 1
    book = []
    name = []
    num = []
    for  item_i, _ in sorted(data.items(), key=operator.itemgetter(1), reverse=True)[0:5500]:
        book.append(item_i)
        title = get_book_info(item_i)
        name.append(title)
        num.append(data[item_i])


    idx = 0
    csvFile=open("data/hotbook_202110_202209.csv",'w',newline='')
    writer=csv.writer(csvFile)
    for i in range(len(book)):
        if idx > 4999:
            break
        if "馆际" in name[i] or "耳机" in name[i] or "教程" in name[i] or "指导" in name[i] or "引论" in name[i] or "数学分析" in name[i] or "高等代数" in name[i] or "考试" in name[i] or "报" in name[i] or "刊" in name[i] or "原理" in name[i]:
            continue
        idx += 1
        writer.writerow((idx, book[i]))
    csvFile.close()


    idx = 0
    csvFile=open("data/hotbook_202110_202209_withname.csv",'w',newline='')
    writer=csv.writer(csvFile)
    for i in range(len(book)):
        if idx > 4999:
            break
        if "馆际" in name[i] or "耳机" in name[i] or "教程" in name[i] or "指导" in name[i] or "引论" in name[i] or "数学分析" in name[i] or "高等代数" in name[i] or "考试" in name[i] or "报" in name[i] or "刊" in name[i] or "原理" in name[i]:
            continue
        idx += 1
        writer.writerow((idx, book[i], name[i], num[i]))
    csvFile.close()
    return


if __name__ == "__main__":
    server = "127.0.0.1"    # 数据库服务器名称或IP
    user = "root"   #  用户名
    month_list = ["202110", "202111", "202112", "202201", "202202", "202203", "202204", "202205", "202206", "202207", "202208", "202209"]
    password = "284284dfl" # 密码
    cur_list = []
    for i in month_list:
        database_month = "userlog_" + i
        print(database_month)
        db_month = pymysql.connect(host=server, user=user, passwd=password, db=database_month)
        cur_list.append(db_month.cursor())
    loadData(cur_list)  # 获得数据