import re
from threading import Thread
from crawler import naverblog
from crawler import navernews
from analyzer import textAnalyzer
from analyzer import renderWordCloud
import matplotlib.pyplot as plt
from analyzer import setCalculus
import os
from os.path import dirname
import pymysql
import multiprocessing
from multiprocessing import Process, Queue, freeze_support
from crawler import dao
import time
from datetime import datetime
from google.cloud import storage

class DataUtil:
    def __init__(self):
        self.a_list = []
        self.b_list = []
        self.input_list = []
        self.base_dir = dirname(dirname(__file__))

        self.font_name = 'NanumSquareR.ttf'
        self.font_dir = '/fonts'
        self.mask_dir = '/img/wordcloud'
        self.task_id = None

    def convert_channel(selt,channel):
        if channel == 'Naver_Blog':
            return 'naverblog'
        elif channel =='Naver_News':
            return 'navernews'
        elif channel =='YouTube':
            return 'youtube'
        elif channel =='Instagram':
            return 'instagram'

    def make_proxy(self, proxy_list):

        req_proxy_list = []
        proxy_id = []
        for index, usable_proxy in enumerate(proxy_list):
            proxy = None
            id, pw, ip, port = usable_proxy['user'], usable_proxy['pass'], usable_proxy['ip'], usable_proxy['port']
            proxy = {'https': 'https://{}:{}@{}:{}'.format(id, pw, ip, port),
                     'http': 'https://{}:{}@{}:{}'.format(id, pw, ip, port)} if not usable_proxy['ip'] == 'root' else proxy
            req_proxy_list.append(proxy)
            proxy_id.append(usable_proxy['id'])
        return req_proxy_list,proxy_id

    def divide_process(self,proxy_id, total_proxy_num):
        PROXY_ID =proxy_id
        TOTAL_PROXY_NUM = total_proxy_num

        while True:
            ##mod : task 번호를 프록시 번호로 나누었을 때 나머지

            mod = PROXY_ID if PROXY_ID<TOTAL_PROXY_NUM else 0
            ##db 연결
            dao_ydns = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                               charset='utf8mb4')

            ##1. proxy_id 로 해당하는 proxy 가져오기
            proxy_rows = dao_ydns.select_proxy(PROXY_ID)

            ##2. 해당 프록시를 list에 담아둔다.
            proxy_list =[]
            for proxy in proxy_rows:
                proxy_list.append(proxy)

            ##3. 요청 들어온 작업을 확인한다. 전체 프록시 개수로 나누었을 때 나머지가 proxy_id 와 같은 요청을 모두 가져옴(전체개수 ==proxy_id 일 때 제외) .
            real_task_rows= []
            task_rows = dao_ydns.select_gr()
            for row in task_rows:
                if row['id']%TOTAL_PROXY_NUM==mod:
                    real_task_rows.append(row)

            ####해당 proxy 가 처리해야할 task 가 있는 경우
            if len(real_task_rows)>0:
                real_task_rows = real_task_rows[:1]
                ### 해당 task 의 id 를 진행중으로 바꿔준다.
                for task in real_task_rows:
                    id =task['id']
                    dao_ydns.update_gi(id)
                input_data = []
                ##7. 요청된 테스크 가져오기
                for task in real_task_rows:
                    try:
                        task_list = self.data_process(task)
                        input_data.append(task_list)
                    except:
                        dao_ydns.update_er(task['id'])
                        continue\
                ##8.proxy 형태 만들어주기
                ##make_proxy
                # input : proxy_list
                # return : req_proxy_list
                req_proxy_list, proxy_id = self.make_proxy(proxy_list)
                for id in proxy_id:
                    dao_ydns.update_N_proxy(id)
                ##9. input_data 에 proxy 넣어주기
                for index, task_list in enumerate(input_data):
                    task_list[0].append(req_proxy_list[0])
                    task_list[0].append(proxy_id[0])

                    task_list[1].append(req_proxy_list[0])
                    task_list[1].append(proxy_id[0])
                for i in input_data:
                    print(i)

                ##10. 쓰레드 돌리기
                threads = [None] * len(input_data) * 2
                results = [None] * len(input_data) * 2

                for index, task_list in enumerate(input_data):
                    for jindex, input_list in enumerate(task_list):
                        print(input_list)
                        threads[2 * index + jindex] = Thread(target=self.to_crawl,
                                                                args=(input_list, results, 2 * index + jindex,req_proxy_list[0]))
                        threads[2 * index + jindex].start()

                for i in range(len(threads)):
                    threads[i].join()
                ##crawling end
                # proxy status : N -> P
                for id in proxy_id:
                    dao_ydns.update_P_proxy(id)

                # 쓰레드 결과 값(TASK ID ) 워드클라우드 생성을 위해 전달
                for index, task_list in enumerate(input_data):
                    for jindex, input_list in enumerate(task_list):
                        input_list.append(results[2 * index + jindex])

                # 워드클라우드 생성
                for task_list in input_data:
                    self.to_venndiagram_wordcloud(task_list)
            else :
                print('해야할작업이 없습니다. 1분간 쉽니다', '현재시각:',datetime.now())
                time.sleep(60)

    def data_process(self,task):

        periodA = task['periodA']
        periodA = re.findall("\d\d\d\d\-\d\d-\d\d", periodA)

        periodB = task['periodB']
        periodB = re.findall("\d\d\d\d\-\d\d-\d\d", periodB)

        startdateA = periodA[0]
        enddateA = periodA[1]

        startdateB = periodB[0]
        enddateB = periodB[1]
        a_list = [task['keywordA'],
                  self.convert_channel(task['channelA']),
                  startdateA,
                  enddateA,
                  task['nUrlA'],
                  task['id']
                  ]

        b_list = [task['keywordB'],
                  self.convert_channel(task['channelB']),
                  startdateB,
                  enddateB,
                  task['nUrlB'],
                  task['id']
                  ]

        input_list = [a_list, b_list]
        self.input_lsit = input_list
        return input_list

    def upload_to_bucket(self, blob_name, path_to_file, bucket_name):
        """ Upload data to a bucket"""

        # Explicitly use service account credentials by specifying the private key
        # file.
        dir_name = "{}/source/creds/".format(self.base_dir)
        storage_client = storage.Client.from_service_account_json(
            dir_name + 'wordcloud_creds.json')
        # print(buckets = list(storage_client.list_buckets())

        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(path_to_file)
        blob.make_public()
        url = blob.public_url
        # returns a public url
        return url


    def to_crawl(self, input_list,results, i, proxy=None):

        keyword = input_list[0]
        channel = input_list[1]
        startdate = input_list[2]
        enddate = input_list[3]
        nUrl = (input_list[4])

        if channel == 'naverblog':
            task_id = naverblog.crawl(keyword, startdate, enddate, int(nUrl), proxy)

        elif channel == 'navernews':
            task_id = navernews.crawl(keyword, startdate, enddate, int(nUrl), proxy)
        else:
            task_id = naverblog.crawl(keyword, startdate, enddate, int(nUrl), proxy)
        results[i]= task_id

    def to_venndiagram_wordcloud(self,task):

        dao_ydns = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                           charset='utf8mb4')

        task_a = task[0]
        task_b = task[1]

        ##task  A 에 관한 작업 수행
        keyword_a = task_a[0]
        channel_a = task_a[1]
        startdate_a = task_a[2]
        enddate_a = task_a[3]
        nUrl_a = task_a[4]
        task_id_a = task_a[8]

        #task_B에 관한 작업 수행
        keyword_b = task_b[0]
        channel_b = task_b[1]
        startdate_b = task_b[2]
        enddate_b = task_b[3]
        nUrl_b = task_b[4]

        task_id_b = task_b[8]

        id = task_a[5]
        proxy_id = task_a[7]

        analyzer_a = textAnalyzer.TextAnalyzer(keyword_a,channel_a,startdate_a, enddate_a, "Mecab", nUrl_a, task_id_a, 'A', id)
        analyzer_b = textAnalyzer.TextAnalyzer(keyword_b,channel_b, startdate_b, enddate_b, "Mecab", nUrl_b, task_id_b, 'B', id)

        #워드클라우드를 위한 텍스트 분석
        dict_a = analyzer_a.extractFrequentWords(500,1)
        dict_b = analyzer_b.extractFrequentWords(500,1)

        #a-b , a & b , b-a
        try:

            sc = setCalculus.setCalc(dict_a, dict_b)
            interdict = sc.getInter()
            differa = sc.getDiff1()
            differb = sc.getDiff2()
            plt.clf()

            ###### 벤다이어그램 ######
            #a & b
            wc5 = renderWordCloud.WordCloudRenderer(interdict, 'brg')
            wc5.setMask("{}/mask_inter.png".format(self.base_dir+self.mask_dir))

            #a - b
            wc6 = renderWordCloud.WordCloudRenderer(differa, 'Dark2')
            wc6.setMask("{}/mask_diff1.png".format(self.base_dir+self.mask_dir))

            #b - a
            wc7 = renderWordCloud.WordCloudRenderer(differb, 'tab10')
            wc7.setMask("{}/mask_diff2.png".format(self.base_dir+self.mask_dir))

            # 교집합그림#
            plt.figure(5, figsize=(16, 12))
            plt.imshow(wc5.getWordCloud(), interpolation='bilinear')
            plt.imshow(wc6.getWordCloud(), interpolation='bilinear')
            plt.imshow(wc7.getWordCloud(), interpolation='bilinear')

            plt.axis('off'), plt.xticks([]), plt.yticks([])
            plt.tight_layout()
            plt.subplots_adjust(left=0, bottom=0, right=1, top=1, hspace=0, wspace=0)

            img_name = str(id) + '.png'
            img_path = '{}/source/inter/{}'.format(self.base_dir, img_name)

            plt.savefig('{}/source/inter/{}'.format(self.base_dir,id), pad_inches=0, dpi=100, transparent=False)
            plt.close()

            dao_ydns.update_wordcloud_path(self.base_dir,str(id)+'.png',str(id))
            img_url = self.upload_to_bucket(img_name, img_path, 'wordcloud_ap')
            dao_ydns.update_img_url(img_url, id)

            dao_ydns.update_gf(id)
            dao_ydns.update_gather_finish(id)
            dao_ydns.update_P_proxy(proxy_id)
            print("{}완료".format(id))

        except Exception as e:
            print(e)
            dao_ydns.update_er(id)
            dao_ydns.update_P_proxy(proxy_id)
