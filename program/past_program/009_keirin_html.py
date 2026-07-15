import requests
from bs4 import BeautifulSoup

url = "https://www.keirin.jp/pc/top"

response = requests.get(url)

soup = BeautifulSoup(response.text, "lxml")

print(response.text[:3000])