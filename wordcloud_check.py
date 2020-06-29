import pymysql
from crawler import navershopping
from crawler import naverblog
from crawler import bigkinds
from crawler import navernews
import re
# from crawler import dao
conn = pymysql.connect(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl', charset= 'utf8mb4')
curs = conn.cursor(pymysql.cursors.DictCursor)


sql_gi = 'select * from polls_breakdown where status=\'%s\' order by create_time asc'%('GI')
sql_gr = 'select * from polls_breakdown where status=\'%s\' order by create_time asc'%('GR')

curs.execute(sql_gi)
rows_gi = curs.fetchall()

curs.execute(sql_gr)
rows_gr = curs.fetchall()

if len(rows_gi)>0:
    print('이미진행중인 작업이 존재합니다.')
elif len(rows_gr)>0:
    print('요청된 작업을 처리합니다.')

    ##작업을 시작합니다.
    # dao.DAO(rows_gr[0])

    keywordA = rows_gr[0]['keywordA']
    keywordB = rows_gr[0]['keywordB']
    channelA = rows_gr[0]['channelA']
    channelB = rows_gr[0]['channelB']
    periodA = rows_gr[0]['periodA']
    periodB = rows_gr[0]['periodB']

    print(periodA)
    periodA = re.findall("\d\d\d\d\-\d\d-\d\d",periodA)
    print(periodA)
    # naverblog.crawl()

# print('sql:{}'.format(sql))
# curs.execute(sql)
# rows = curs.fetchall()
# print(rows[0])
# # if rows['']