from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import requests
CUSTOM_HEADER = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, utf-8',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cookie': 'NNB=26JKENAB5VNFY; npic=LW1n/Y7lr1485twRJiDAu7IQNma7Byg1+eD1dujBnEarfw1Jj92XPcGCQrmTmIkDCA==; _ga=GA1.2.785938604.1550973896; nx_ssl=2; BMR=; _naver_usersession_=ldZTind9DyvToDWTHUQkNw==; page_uid=UfWJIwprvOsssOBmEzdssssstul-404192; JSESSIONID=FE270C9B4B35C84D83479B52E6020831.jvm1',
    'referer': '',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'}
real_proxies = []
def make_proxy():
  #UserAgent 생성
  ua = UserAgent()  # From here we generate a random user agent
  proxies = []  # Will contain proxies [ip, port]


  # Retrieve latest proxies
  print('''
  #######프록시 가져오기 시작#########
  ''')
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')
  header = CUSTOM_HEADER
  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })
  print('프록시 개수 :',len(proxies))
  print('''
  #############프록시 가져오기 끝############
  ''')
  delete_n = 0
  for index,proxy in enumerate(proxies):

    prox = {
      "http": 'http://' + proxy['ip'] + ':' + proxy['port'],
      "https": 'http://' + proxy['ip'] + ':' + proxy['port']
    }
    # Make the call
    try:
        print(index,':',prox)
        req = requests.get("https://section.blog.naver.com/", proxies=prox,timeout=2, headers=header)
        print(req.status_code)
        print('##프록시 설정 끝')
        # Every 10 requests, generate a new proxy
        if req.status_code==200:
            my_ip = prox['https']
            print('#my_ip_' + str(index) + ': ' + my_ip,'_',req.content)
            real_proxies.append(my_ip)
    except Exception as e: # If error, delete this proxy and find another one
        print(e)
        print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')

    print('next')
  return real_proxies

if __name__ == '__main__':
    real_proxies = make_proxy()
    print(real_proxies)