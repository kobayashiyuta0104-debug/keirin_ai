import requests

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text

index = html.find("naibu")

print(index)
print(html[index:index+500])