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
from api_proxy import make_proxy
import multiprocessing
from crawler import dao

def main() :
    tmp_proxy_list = []

    ##db 연결
    dao_ydns = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                       charset='utf8mb4')

    ##1. 사용가능한 프록시 갯수 확인하기 , 어떤 서버에서 가져올지 parameter 로 넘겨주기
    proxy_rows = dao_ydns.select_check_proxy(server='ydns')
    ##2. 사용가능한 프록시의 id를 list에 담아둔다.
    for proxy in proxy_rows:
        tmp_proxy_list.append(proxy)

    ##3. 요청 들어온 작업을 확인한다. 요청은 프록시 개수보다 작거나 같음.
    task_rows = dao_ydns.select_gr(len(proxy_rows))
    ##4. 다시 요청의 개수만큼 프록시 사이즈를 맞춰준다.
    proxy_list = tmp_proxy_list[:len(task_rows)]

    ####여기서 if 로 프록시 있으면 하고 없으면 하지말기로 체크하기

    print('---------------')

    if len(proxy_rows)>0:
        ##5. 사용하고 있는 프록시의 상태를 N 으로 변경해준다
        for proxy in proxy_list:
            id = proxy['id']
            dao_ydns.update_N_proxy(id)

        for task in task_rows:
            id = task['id']
            dao_ydns.update_gi(id)
            dao_ydns.update_gather_start(id)
        ##6. input_data 만들기
        input_data = []

        ##7. 요청된 테스크 가져오기
        for task in task_rows:
            dt = data_util.DataUtil()
            task_list = dt.data_process(task)
            input_data.append(task_list)

        ##8.proxy 형태 만들어주기
        ##make_proxy
        # input : proxy_list
        # return : req_proxy_list
        dt = data_util.DataUtil()
        req_proxy_list, proxy_id = dt.make_proxy(proxy_list)

        ##9. input_data 에 proxy 넣어주기
        for index, task_list in enumerate(input_data):
            task_list[0].append(req_proxy_list[index])
            task_list[0].append(proxy_id[index])

            task_list[1].append(req_proxy_list[index])
            task_list[1].append(proxy_id[index])

        for i in input_data:
            print(i)

        ##10. input 데이터를 이용해서 threading 하기
        # def multiprocessing
        num_process = len(proxy_list) * 2
        return num_process, input_data

if __name__ == '__main__':

        ##main 함수 시작
        num_process, input_data = main()

        ##멀티프로세싱 크롤링 시작
        freeze_support()
        processes = [None] * num_process
        manager = multiprocessing.Manager()
        results = manager.list(range(num_process))
        dt = data_util.DataUtil()
        # 모든 스레드를 각각 시작한다.
        for index, task_list in enumerate(input_data):
            for jindex, input_list in enumerate(task_list):
                print(input_list)
                processes[2 * index + jindex] = Process(target=dt.to_crawl,
                                                        args=(input_list, results, 2 * index + jindex))
                processes[2 * index + jindex].start()

        for i in range(len(processes)):
            processes[i].join()

        # 쓰레드 결과 값(TASK ID ) 워드클라우드 생성을 위해 전달
        for index, task_list in enumerate(input_data):
            for jindex, input_list in enumerate(task_list):
                input_list.append(results[2 * index + jindex])

        # 워드클라우드 생성
        for task_list in input_data:
            dt.to_venndiagram_wordcloud(task_list)

