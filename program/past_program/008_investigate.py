import requests

url = "https://www.keirin.jp/pc/top"

response = requests.get(url)

print(response.status_code)
print(response.url)
print(response.headers["content-type"])