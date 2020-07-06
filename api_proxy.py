import requests

def make_proxy(input_data):

    ###api 요청해서 proxy 리스트 가져오기
    api_key ='5daef4ee22-3a5ac52786-f292d0ecca'
    method ='getproxy'
    params = None

    url ='https://proxy6.net/api/{}/{}/?{}'.format(api_key, method, params)
    response =requests.get(url)
    response_to_json = response.json()
    n = 0

    ###첫번째 proxy 는 기본 proxy 로 None 을 설정한다.
    tmp_proxy_list = [None]

    ###개인 proxy 리스트 를 가져와서 프록시 목록에 추가해준다
    for index, (key,usable_proxy) in enumerate(response_to_json['list'].items()):
        if usable_proxy['version']=='4':
            id,pw,ip,port = usable_proxy['ip'],usable_proxy['port'],usable_proxy['user'],usable_proxy['pass']
            proxy = {'https': 'https://{}:{}@{}:{}'.format(id,pw,ip,port),
                'http': 'https://{}:{}@{}:{}'.format(id,pw,ip,port)}
            tmp_proxy_list.append(proxy)

    ###input_data 개수와 proxy 리스트를 맞춰준다.
    proxy_list = tmp_proxy_list[:len(input_data)]

    ##input_data 에 프록시 넣어주기
    for index, task_list in enumerate(input_data):
        task_list[0].append(proxy_list[index])
        task_list[1].append(proxy_list[index])
    return input_data