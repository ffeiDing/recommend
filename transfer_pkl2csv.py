import pickle
import csv

def load_dic(name):
    with open(name, 'rb') as f:
        return pickle.load(f)

csvFile=open("data/recommend_202211.csv",'w',newline='')
writer=csv.writer(csvFile)
writer.writerow(("user_id", "ckey_list"))

data = load_dic("data/recommend_202211.pkl")

for user_id, recommend in data.items():
    writer.writerow((user_id, recommend["ckey_list"]))

csvFile.close()

