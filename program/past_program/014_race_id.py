import requests

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text

print(html.find("kaisaiDate"))
print(html.find("naibukeirinCd"))
print(html.find("raceNum"))