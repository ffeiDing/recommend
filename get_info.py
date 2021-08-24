# 获取书籍的信息

import requests

url = "http://162.105.134.104/circulation-log?itemBarcode=5954378e-8ec0-465f-88d9-5a16f7c4f56a"
response = requests.get(url)
print(response.headers)

print(response.text)

