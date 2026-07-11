import requests
url = "https://keirin.jp/pc/top"
response = requests.get(url)
html = response.text
index = html.find("函館")
print(index)
print(html[index-500:index+500])