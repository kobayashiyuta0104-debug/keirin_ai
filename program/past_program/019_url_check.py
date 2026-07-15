import requests

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text

print(html.find("racecard"))
print(html.find("shutsuba"))
print(html.find("raceindex"))
print(html.find("/pc/race"))
print(html.find("raceNo"))