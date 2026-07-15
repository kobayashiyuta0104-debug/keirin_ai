import requests
from bs4 import BeautifulSoup
url = "http://www.python.org"
response=requests.get(url)
soup=BeautifulSoup(response.text,"lxml")
print(soup.title.text)