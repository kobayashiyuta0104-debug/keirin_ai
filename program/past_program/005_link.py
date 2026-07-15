import requests
from bs4 import BeautifulSoup
url = "https://www.python.org"
response = requests.get(url)
soup = BeautifulSoup(response.text,"lxml")
links = soup.find_all("a")
print("リンク数",len(links))
for link in links[:10]:
    print(link.text.strip())