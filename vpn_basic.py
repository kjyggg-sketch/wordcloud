from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]

# Main function
def random_proxy():
  return random.randint(0, len(proxies) - 1)

def main():
  # Retrieve latest proxies
  print('''
  #######프록시 가져오기 시작#########
  ''')
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')

  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })

  # Choose a random proxy
  proxy_index = random_proxy()
  proxy = proxies[proxy_index]
  print('''
  #############프록시 가져오기 끝############
  ''')
  for n in range(1, 100):
    print('n번째',n)
    req = Request('https://www.google.com/')
    req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')
    print('##프록시 설정 끝')
    # Every 10 requests, generate a new proxy
    if n % 10 == 0:
      print('n:',n)
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

    # Make the call
    try:
      print('try 진입')
      my_ip = urlopen(req).read().decode('utf8')
      print('#my_ip_' + str(n) + ': ' + my_ip)
    except Exception as e: # If error, delete this proxy and find another one
      print(e)
      del proxies[proxy_index]
      print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]
    print('다음')
# Retrieve a random index proxy (we need the index to delete it if not working)

if __name__ == '__main__':
  main()