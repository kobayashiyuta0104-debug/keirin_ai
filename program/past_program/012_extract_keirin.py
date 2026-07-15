import requests
import re

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text
places = re.findall(r'"keirinjoName":"(.*?)"',html)

print(places)