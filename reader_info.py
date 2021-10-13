import pickle

def save_dic(name, dic):
    with open(name, 'wb') as f:
        pickle.dump(dic, f, pickle.HIGHEST_PROTOCOL)

reader = {}
f1 = open("data/student.txt","r") 
f2 = open("data/teacher.txt","r") 
lines = f1.readlines()+f2.readlines()      #读取全部内容 ，并以列表方式返回
for line in lines:
    if line.startswith("北") or line.startswith("医"):
        # print(line)
        line.replace("||", "|")
        row = line.split("|")
        # print(row)
        if len(row) < 6:
            continue
        user_id = row[3]
        reader.setdefault(user_id,{})
        reader[user_id]["school"] = row[2]
        reader[user_id]["name"] = row[4]
        reader[user_id]["gender"] = row[5]
        reader[user_id]["lib"] = row[0]
        reader[user_id]["type"] = row[1]

save_dic("data/reader_info.pkl", reader)
print(reader)
          


# daka = {}
# first_row = True
# for row in worksheet.rows:
#     if first_row:
#         first_row = False
#         continue
#     user_id = row[1].value
#     daka.setdefault(user_id,{})
#     level = row[2].value
#     daka[user_id][level] = 1
#     if level == 3:
#         daka[user_id]["book_name"] = 4

# daka_cnt = [0 for i in range(6)]
# for key, user_info in daka.items():
#     meet_all = True
#     for i in range(5):
#         if i+1 in user_info.keys():
#             daka_cnt[i] += 1
#         else:
#             meet_all = False
#     if meet_all == True:
#         daka_cnt[5] += 1

# print("参与人数：", len(daka))
# print("全部通关人数：", daka_cnt[5])
# for i in range(5):
#     print("通过第" + str(i+1) + "关的人数：", daka_cnt[i])

