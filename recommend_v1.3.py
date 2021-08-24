# 借书历史根据时间加权

from math import sqrt
import operator
import pymysql
import pickle
from sql_test import get_recommend_book, get_user_history, get_recommend_book_by_ckey, get_user_history_by_ckey


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
def recommandList(data, W, user, k=3, N=10):
    rank = {}
    book_weight = 1.0/len(data[user])
    idx = 1
    for item_i, item_i_score in data[user].items():  # 获得用户user历史记录，如A用户的历史记录为{'a': '1', 'b': '1', 'd': '1'}
        # print(item_i)
        for item_j, sim_value in sorted(W[item_i].items(), key=operator.itemgetter(1), reverse=True)[0:k]:  # 获得与图书i相似的k本图书
            if item_j not in data[user].keys():  # 该相似的图书不在用户user的记录里
                rank.setdefault(item_j, 0)
                rank[item_j] += float(item_i_score) * sim_value * (idx * book_weight + 1)
        idx = idx + 1

    print("----4.为某个用户推荐----")
    return sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[0:N]


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
        data = load_dic("data/data_v1.3.pkl")
        W = load_dic("data/W_v1.3.pkl")
    else:
        db = pymysql.connect(host=server, user=user, passwd=password, db=database)
        cur = db.cursor()
        data = loadData(cur)  # 获得数据
        save_dic("data/data_v1.3.pkl", data)
        W = similarity(data)  # 计算图书相似矩阵
        save_dic("data/W_v1.3.pkl", W)
        print("---已保存数据---")
    # user_id = "00639061"
    user_id = "1606191027" # "1606191027" # "0006171162"
    recommend_book_ckey_list = recommandList(data, W, user_id, 10, 40)  #推荐
    # recommend_book_id_list =  [('21101000439289', 0.75), ('21101002118423', 0.75), ('21101001488427', 0.7071067811865475), ('21101000256996', 0.7071067811865475), ('21101001507803', 0.7071067811865475), ('21101001507797', 0.7071067811865475), ('21101040025888', 0.6666666666666666), ('21101040073213', 0.6324555320336759), ('21101001934818', 0.6324555320336759), ('21101000655750', 0.5773502691896258)]
    history_book_title_list = get_user_history_by_ckey(user_id)
    recommend_book_title_list = get_recommend_book_by_ckey(recommend_book_ckey_list)
    print("借书历史：")
    print_list(history_book_title_list)
    print(len(history_book_title_list))
    print()
    print("推荐书单：")
    print_list(recommend_book_title_list)

# 80w [('21101002092956', 1.6329931618554523), ('21101002118423', 0.8164965809277261), ('21101001947838', 0.5163977794943222)]

# 160w [('21101000373293', 1.1547005383792517), ('21101000374624', 1.0850712541957748), ('21101002092956', 0.9078403012630165), ('21101001768233', 0.9078403012630165), ('90100040012286', 0.7071067811865475), ('21101040129855', 0.7071067811865475), ('21101040074432', 0.7071067811865475), ('21101000983261', 0.7071067811865475), ('21101000918749', 0.7071067811865475), ('21101001774880', 0.7071067811865475)]

# 230w [('21101002118423', 0.75), ('21101000256996', 0.7071067811865475), ('21101000439289', 0.6666666666666666), ('21101001990554', 0.6666666666666666), ('21101040073213', 0.6324555320336759), ('21101001934818', 0.6324555320336759), ('21101001169419', 0.5773502691896258), ('21101040008014', 0.5773502691896258), ('21101000261292', 0.5773502691896258), ('21101001599168', 0.5163977794943222)]

# 260w [('21101000439289', 0.75), ('21101002118423', 0.75), ('21101001488427', 0.7071067811865475), ('21101000256996', 0.7071067811865475), ('21101001507803', 0.7071067811865475), ('21101001507797', 0.7071067811865475), ('21101040025888', 0.6666666666666666), ('21101040073213', 0.6324555320336759), ('21101001934818', 0.6324555320336759), ('21101000655750', 0.5773502691896258)]
