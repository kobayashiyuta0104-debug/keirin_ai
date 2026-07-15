import requests
import re

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text
pattern = r'"naibuKeirinCd":"(.*?)".*?"keirinjoName":"(.*?)".*?"raceNum":"(.*?)".*?"denTime":"(.*?)".*?"'

races = re.findall(pattern,html)

print("取得件数",len(races))
print()

for race in races:
    print(race)