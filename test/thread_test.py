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
from multiprocessing import Process, Queue
from api_proxy import make_proxy
import multiprocessing


def to_crawl(input_list, results, i,proxy=None):
    task_id = None
    keyword = input_list[0]
    channel = input_list[1]
    startdate = input_list[2]
    enddate = input_list[3]
    nUrl = (input_list[4])
    print('nUrl_type:', type(nUrl))
    print(channel)
    if channel == 'naverblog':
        task_id = naverblog.crawl(keyword, startdate, enddate, int(nUrl), proxy)
    elif channel == 'navernews':
        task_id = navernews.crawl(keyword, startdate, enddate, int(nUrl), proxy)
    results[i]=task_id

if __name__=='__main__':
    conn = pymysql.connect(host='103.55.190.32', user='wordcloud', password='word6244!@', db='crawl', charset='utf8mb4')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    sql = "select * from polls_breakdown where status=\'%s\' limit 5"%('GR')
    curs.execute(sql)
    rows = curs.fetchall()
    input_data = []

    ###요청된 테스크 가져오기
    for row_gr in rows:
        dt = data_util.DataUtil(row_gr)
        task_list = dt.data_process()
        input_data.append(task_list)

    ###api 이용해서 사용가능한 개인 IP 가져오기(proxy 우회)
    input_data=make_proxy(input_data)

    Processes = [None] * len(rows)*2
    manager = multiprocessing.Manager()
    results = manager.list(range(len(rows)*2))

    #모든 스레드를 각각 시작한다.
    for index, task_list in enumerate(input_data):
        for jindex, input_list in enumerate(task_list):
            print(input_list)
            Processes[2*index+jindex] = Process(target=to_crawl, args=(input_list, results, 2*index+jindex))
            Processes[2*index+jindex].start()

    for i in range(len(Processes)):
        Processes[i].join()
    #워드클라우드 생성

    #쓰레드 결과 값(TASK ID ) 워드클라우드 생성을 위해 전달
    for index, task_list in enumerate(input_data):
        for jindex, input_list in enumerate(task_list):
            input_list.append(results[2*index+jindex])

    print('final_input_data',input_data)

