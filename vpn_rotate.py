import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

def random_proxy():
  return random.randint(0, len(proxies) - 1)

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]
CUSTOM_HEADER = {
  'accept': 'application/json, text/plain, */*',
  'accept-encoding': 'gzip, deflate, br, utf-8',
  'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
  'cookie': 'NNB=26JKENAB5VNFY; npic=LW1n/Y7lr1485twRJiDAu7IQNma7Byg1+eD1dujBnEarfw1Jj92XPcGCQrmTmIkDCA==; _ga=GA1.2.785938604.1550973896; nx_ssl=2; BMR=; _naver_usersession_=ldZTind9DyvToDWTHUQkNw==; page_uid=UfWJIwprvOsssOBmEzdssssstul-404192; JSESSIONID=FE270C9B4B35C84D83479B52E6020831.jvm1',
  'referer': 'https://section.blog.naver.com/Search/Post.nhn?pageNo=1&rangeType=ALL&orderBy=sim&keyword=',  # +heyhex
  'user-agent': ua.random}

# Retrieve latest proxies

url = 'https://www.sslproxies.org/'
custom_header = CUSTOM_HEADER
proxies_req = requests.get(url)
proxies_doc = proxies_req.content
print(proxies_doc)

soup = BeautifulSoup(proxies_doc, 'html.parser')
proxies_table = soup.find(id='proxylisttable')

# Save proxies in the array
print(proxies_table)
for row in proxies_table.tbody.find_all('tr'):
  proxies.append({
    'ip':   row.find_all('td')[0].string,
    'port': row.find_all('td')[1].string
  })

# Choose a random proxy
proxy_index = random_proxy()
proxy = proxies[proxy_index]

for n in range(1, 100):
  proxies = {
     "http": 'http://' + proxy['ip'] + ':' + proxy['port'],
     "https": 'http://' + proxy['ip'] + ':' + proxy['port']
  }
  req = requests.get("https://www.google.com/", proxies=proxies)

  # Every 10 requests, generate a new proxy
  if n % 10 == 0:
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]

  # Make the call
  try:
    my_ip = req.content
    print('#' + str(n) + ': ' + my_ip)
  except: # If error, delete this proxy and find another one
    del proxies[proxy_index]
    print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
    proxy_index = random_proxy()
    proxy = proxies[proxy_index]

# Retrieve a random index proxy (we need the index to delete it if not working)
