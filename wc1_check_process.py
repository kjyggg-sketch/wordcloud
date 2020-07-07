from crawler import dao
import requests
import re
import wc2_run_process
url = "http://checkip.dyndns.org"

response = requests.get(url)
server_name = response.text
server_name = re.findall(r'[0-9]+(?:\.[0-9]+){3}',server_name)
server_name = server_name[0]
###각 서버의 IP 주소 가져오기

###IP 주소로 DB 에서 해당 서버 가져오기
dao_ydns = dao.DAO()
server = dao_ydns.check_process(server_name)

###서버가 현재 프로세스 진행중이라면
if server['status']=="OUT":
    dao_ydns.update_process_IN(server_name)
    wc2_run_process.main()
    # dao_ydns.update_process_OUT(server_name)
