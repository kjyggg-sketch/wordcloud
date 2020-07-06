import requests
api_key ='5daef4ee22-3a5ac52786-f292d0ecca'
method ='getproxy'
params = None

url ='https://proxy6.net/api/{}/{}/?{}'.format(api_key, method, params)
response =requests.get(url)
response_to_json = response.json()

for index, (key, usable_proxy) in enumerate(response_to_json['list'].items()):
    if usable_proxy['version'] == '4':
        id, pw, ip, port = usable_proxy['ip'], usable_proxy['port'], usable_proxy['user'], usable_proxy['pass']
        print(id, pw, ip, port)

