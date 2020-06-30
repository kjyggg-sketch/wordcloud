import pymysql
from crawler import navershopping
from crawler import naverblog
from crawler import bigkinds
from crawler import navernews
import re
import multiprocessing
import parmap
from threading import Thread
from crawler import dao
from crawler import data_util
from queue import Queue
import concurrent.futures

##ydns dao 객체 생성
dao_ydns = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl', charset= 'utf8mb4')

#작업중인 요청 체크
row_gi = dao_ydns.select_gi()

##요청 처리하기(선입선출)
row_gr = dao_ydns.select_gr()

##만약 작업중인게 있다면
if len(row_gi)>0:
    print('이미진행중인 작업이 존재합니다.')
    pass
elif len(row_gr)==0:
    print('요청작업이 없습니다')
#작업중인게 없고 요청들어온게 있으면
elif len(row_gr)>0:
    try:
        print('요청된 작업을 처리합니다.')
        ##작업을 시작합니다.
        task = row_gr[0]

        ##작업 상태를 업데이트 시켜주기
        dao_ydns.update_gi(task['id'])

        #task : dictionary 타입 keyword:'', channel: '', perioda=['',''] etc
        #task 를 처리하기 위해 data util 객체를 생성합니다.
        dt = data_util.DataUtil(task)

        #task 를 thread 처리 하기 위해 input_data 로 만들어줍니다.
        input_data = dt.data_process()


        #dt.to_crawl 입력받은 데이터를 크롤링 엔진으로 전달

        #threading 생성
        threads = [None] * len(input_data)
        results = [None] * len(input_data)

        #모든 스레드를 각각 시작한다.
        for index, input_list in enumerate(input_data):
            threads[index] = Thread(target=dt.to_crawl, args=(input_list, results, index))
            threads[index].start()
        #쓰레드 종료
        for i in range(len(threads)):
            threads[i].join()
        #워드클라우드 생성

        #쓰레드 결과 값(TASK ID ) 워드클라우드 생성을 위해 전달
        for index,input_list in enumerate(input_data):
            input_list.append(results[index])
        print('final_input_data',input_data)

        dt.to_venndiagram_wordcloud(input_data)

        #마무으리
        dao_ydns.update_gf(task['id'])
    except Exception as e:
        print('{} is happen'.format(e))
        dao_ydns.update_er(task['id'])
        dao_ydns.close()