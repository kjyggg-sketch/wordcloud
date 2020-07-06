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
import multiprocessing
from multiprocessing import Process, Queue, freeze_support
from crawler import dao
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


    def to_crawl(self, input_list,results, i, proxy=None):

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
        else:
            task_id = naverblog.crawl(keyword, startdate, enddate, int(nUrl), proxy)
        results[i]= task_id

    def to_venndiagram_wordcloud(self,task):
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
        sc = setCalculus.setCalc(dict_a, dict_b)
        interdict = sc.getInter()
        differa = sc.getDiff1()
        differb = sc.getDiff2()
        dao_ydns  = dao.DAO(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                               charset='utf8mb4')

        try:
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

            plt.savefig('{}/source/inter/{}'.format(self.base_dir,id), bbox_inces='tight', pad_inches=0, dpi=100, transparent=False)
            plt.show()

            dao_ydns.update_wordcloud_path(self.base_dir,str(id)+'.png',str(id))
            dao_ydns.update_gf(id)
            dao_ydns.update_gather_finish(id)
            dao_ydns.update_P_proxy(proxy_id)

        except Exception as e:
            print(e)
            dao_ydns.update_er(id)
            dao_ydns.update_P_proxy(proxy_id)
