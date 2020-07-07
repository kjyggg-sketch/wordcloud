from threading import Thread
import re
from crawler import naverblog
from crawler import navernews
from analyzer import textAnalyzer
from analyzer import renderWordCloud
import matplotlib.pyplot as plt
from analyzer import setCalculus
import os
from os.path import dirname
import pymysql
from crawler import data_util
from multiprocessing import Process, Queue, freeze_support
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing
from crawler import dao

def main():

    ### 0. 연결할 DB 설정
    dt = data_util.DataUtil()
    process_list=[]
    dao_ydns = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                       charset='utf8mb4')
    ### 1. 서버명을 정해준다.
    server = 'ydns'

    ### 2. 서버에 해당하는 프록시 정하기
    selected_proxy_rows = dao_ydns.select_sever_proxy(server)

    ### 3. 모든 프록시 개수 가져오기
    total_proxy_rows = dao_ydns.select_total_proxy()
    total_proxy_num = len(total_proxy_rows)
    proxy_id_list = []
    for proxy_row in selected_proxy_rows:
        proxy_id_list.append(proxy_row['id'])
    min_proxy_id = min(proxy_id_list)
    max_proxy_id = max(proxy_id_list)

    ### 4. 프록시에 해당하는 프로세스를 만들어준다.
    # 프록시는 자신의 고유 번호(id) 를 가진다.  ex) 1,2,3,4
    # 전체 프록시 길이로 task num 을  나누었을 때 나머지가 프로세스가 할당받은 아이디와 같은 task 만 처리한다
    # ex) 전체길이가 12 이고 process 가 할당받은 id 가 5라면 이 process가 처리하는 작업은 5, 17, 29, 41
    # 각각의 프로세스는 한번에 여러개의 task 를 처리할 수 있지만 프로세스 별로 task 가 중복될 수 없다.
    # 가령 id가 5인 process 는 항상 id가 6인 process 와 처리하는 작업이 다르다.
    for proxy_id in range(min_proxy_id,max_proxy_id+1):
        dt = data_util.DataUtil()
        process = Process(target=dt.divide_test, args=(proxy_id,total_proxy_num),)##프로세스의 고유 id(proxy_id) 와 전체 길이를 넘겨준다.
        process_list.append(process)

    print("process시작")
    for process in process_list:
        process.start()

if __name__ == '__main__':
    main()