import re
import pymysql
import time
from collections import Counter
from konlpy.tag import Okt
from konlpy.tag import Kkma
from konlpy.tag import Komoran
from konlpy.tag import Hannanum
from eunjeon import Mecab
from konlpy.tag import Twitter
from operator import itemgetter
import pandas as pd
import gc
import os

class TextAnalyzer:

    def __init__(self, keyword,channel, startDate, endDate, nlpEngine, nUrl, task_id, category, id):

        self.keyword = keyword

        self.channel = channel
        self.startDate = startDate
        self.endDate = endDate

        self.nlpEngine = nlpEngine

        self.nUrl = nUrl
        self.task_id = task_id
        self.id = id
        self.category = category
        if nlpEngine == "Okt":
            self.konlpy = Okt()
        elif nlpEngine == "Komoran":
            self.konlpy = Komoran()
        elif nlpEngine == "Kkma":
            self.konlpy = Kkma()
        elif nlpEngine == "Hannanum":
            self.konlpy = Hannanum()
        elif nlpEngine == "Mecab":
            self.konlpy = Mecab()
        elif nlpEngine == "Twitter":
            self.konlpy = Twitter()
        else:
            self.konlpy = Okt()

    def read(self):
        table = 'cdata'
        conn = pymysql.connect(host='106.246.169.202', user='root', password='robot369',
                               db='dalmaden', charset='utf8mb4')
        # 106.246.169.202
        # 192.168.0.105
        # 103.55.190.32 wordcloud ap
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = "select * from %s where (keyword=\'%s\') and channel=\'%s\' and post_date>=\'%s\' and post_date<=\'%s\' and task_id=\'%s\' limit %d" % \
              (table,self.keyword, self.channel ,self.startDate, self.endDate, self.task_id ,self.nUrl)
        print('sql=', sql)
        curs.execute(sql)

        rows = curs.fetchall()
        self.text_list = []
        self.text = ''
        print(self.keyword, len(rows))
        for row in rows:
            self.text +=row['text']
            self.text_list.append(row['text'])
        conn.close()

    def cleanse(self):
        self.text = self.text.replace(self.keyword, ' '+self.keyword)
        self.text = re.sub(u"(http[^ ]*)", " ", self.text)
        self.text = re.sub(u"@(.)*\s", " ", self.text)
        self.text = re.sub(u"#", "", self.text)
        self.text = re.sub(u"\\d+", " ", self.text)
        self.text = re.sub(u"[^가-힣A-Za-z]", " ", self.text)
        self.text = re.sub(u"\\s+", " ", self.text)
    def removeCommonWords(self):
        if self.channel == "Instagram":
            self.keywordList = ["인스타그램", "인스타", "팔로우", "맞팔", "인친", "셀스타그램", "그램", "스타","행복","일상","오늘","소통"]
        if self.channel == "naverblog":
            self.keywordList = ["포스팅", "블로그", "댓글", "이웃추가"]
        if self.channel == "Twitter":
            self.keywordList = ["트윗", "RT", "트위터"]
        if self.channel == "navernews":
            self.keywordList = ["없음", "헤럴드", "역필", "투데이", "머니", "코리아", "기자", "오마이", "구독", "연합", "채널", "네이버", "뉴시스",
                                "금지", "저작", "무단", "뉴스", "재배포"]


        for keyword in self.keywordList:

            self.text = self.text.replace(keyword, "")

    def posTag(self):
        print("Getting Meaningful Words for " + self.keyword + "...", end="\t")
        pos = list()
        for text in self.text_list:
            pos.extend(self.konlpy.pos(text))
        print("Pos tagging complete. Extracting Nouns, Adjectives, Exclamations ...")
        words = []
        for p in pos:
            if p[1] in ['NNG','NNP']:  # 코모란, Mecab 기준임
            #'MAG'
            #if p[1] in ['IC','VA']:  # 코모란, Mecab 기준임
                # 'VA', 'IC' 위에 대괄호 안에 추가하면 된다
                # if p[1] in ['Noun', 'ProperNoun']:  # Okt, Twitters
                # 'Noun', 'ProperNoun', 'Adjective', 'Exclamation' 위에 대괄호 안에 추가하면 된다!
                words.append(p[0])

        print("Extracting complete.")

        return words

    def func(self, x):
        if x[1] > 1:
            return x
        else:
            return None

    def getWordCount(self, nRank, minFreq):
        words = self.posTag()

        counter = Counter(words)
        # self.wordDict = counter
        c = counter.most_common(nRank)
        c = list(filter(lambda x: len(x[0]) >= 2, c))

        db_diction = {}
        compare_list = []  # 비교대상 년도의 빈도수를 뽑는다
        q = 0
        for i in c:
            # compare_dict = {'keyword': i[0], 'count':i[1], 'basic_differentiate': 1 if i[0] in basic_keylist else 0}       #기준년도 keylist 와 일치하는 keyword 를 찾고 식별값을 부여한다(일치: 1 불일치: 0)
            # compare_list.append(compare_dict)
            compare_dict = {'keyword': i[0], 'count': i[1]}  # 기준년도 keylist 와 일치하는 keyword 를 찾고 식별값을 부여한다(일치: 1 불일치: 0)
            compare_list.append(compare_dict)
            # list에 추가한다.

            # DB에 추가하기 위해 사전 {'K': 'V'} 사전 형태 만들어주기
            if q < 300:
                db_diction[i[0]] = i[1]
            q += 1

        db_diction = str(db_diction)
        db_diction = db_diction.replace("'", "")

        ##DB 에 키워드와 빈도수 리스트 저장하기
        db = 'crawl'
        conn = pymysql.connect(host='103.55.190.32', user='wordcloud', password='word6244!@',
                               db=db, charset='utf8mb4')
        # 106.246.169.202
        # 192.168.0.105
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = "insert into polls_keyword_number(polls_id,keyword, category ,channel, stdate, endate, nurl, top300)" \
              + "values (\'%s\',\'%s\',\'%s\',\'%s\', \'%s\',\'%s\', %d, \'%s\')" % \
              (self.id, self.keyword, self.category, self.channel, self.startDate, self.endDate, self.nUrl, db_diction)
        curs.execute(sql)
        conn.commit()
        conn.close()
        c.sort(key=itemgetter(1), reverse=True)

        self.freqWordList = []
        nWord = 0
        for i in c:
            if i[1] < minFreq:
                break
            self.freqWordList.append(i)
            nWord += 1
            if nWord >= nRank:
                break
        self.freqWordDict = dict(self.freqWordList)


    def extractFrequentWords(self, nRank, minOccur):
        self.read()
        self.cleanse()
        self.removeCommonWords()
        self.getWordCount(nRank, minOccur)
        return self.freqWordDict
