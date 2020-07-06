import re

from threading import Thread
import pymysql
from datetime import datetime
class DAO:
    def __init__(self, host='103.55.190.32', port=3306,  user='wordcloud', password='word6244!@', db='crawl', charset='utf8mb4'):

        self.conn = pymysql.connect(host='103.55.190.32', port=3306, user='wordcloud', password='word6244!@', db='crawl',
                               charset='utf8mb4')
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.close = self.conn.close


    def select_gr(self, proxy_num):
        sql_gr = "select * from polls_breakdown where status=\'%s\' order by create_time asc limit %s " % ('GR',proxy_num)
        self.curs.execute(sql_gr)
        rows_gr = self.curs.fetchall()
        return rows_gr

    def select_gi(self):
        sql_gi = 'select * from polls_breakdown where status=\'%s\' order by create_time asc' % ('GI')
        self.curs.execute(sql_gi)
        rows_gi = self.curs.fetchall()
        return rows_gi

    def select_check_proxy(self,server):
        select_check_proxy = "select * from server_proxy where server=\'%s\' and status=\'%s\'" % (server, 'P')
        self.curs.execute(select_check_proxy)
        rows_gi = self.curs.fetchall()
        return rows_gi

    def update_gi(self,id):
        sql_update_gi = "update polls_breakdown set status=\'%s\' where id =\'%s\'"%('GI',id)
        print(sql_update_gi)
        self.curs.execute(sql_update_gi)
        self.conn.commit()

    def update_gf(self,id):
        sql_update_gf = "update polls_breakdown set status=\'%s\' where id =\'%s\'"%('GF',id)
        self.curs.execute(sql_update_gf)
        self.conn.commit()
        pass

    def update_er(self,id):
        sql_update_er = "update polls_breakdown set status=\'%s\' where id =\'%s\'"%('ER',id)
        self.curs.execute(sql_update_er)
        self.conn.commit()
        pass

    def update_gather_start(self,id):
        sql_update_er = "update polls_breakdown set gather_st_time=\'%s\' where id =\'%s\'"%(datetime.now(),id)
        self.curs.execute(sql_update_er)
        self.conn.commit()
        pass
    def update_gather_finish(self,id):
        sql_update_er = "update polls_breakdown set gather_en_time=\'%s\' where id =\'%s\'"%(datetime.now(),id)
        self.curs.execute(sql_update_er)
        self.conn.commit()
        pass

    def update_P_proxy(self,id):
        sql_update_n_proxy = "update server_proxy set status=\'%s\' where id=%s" % ('P', id)
        self.curs.execute(sql_update_n_proxy)
        self.conn.commit()
        pass
    def update_N_proxy(self,id):
        sql_update_n_proxy = "update server_proxy set status=\'%s\' where id=%s" % ('N', id)
        self.curs.execute(sql_update_n_proxy)
        self.conn.commit()
        pass
    def update_wordcloud_path(self,base_dir,wordcloud,id):
        update_wordcloud_path = "update polls_breakdown set saved_path=\'%s\',saved_name=\'%s\' where id=%s"%('{}/source/inter'.format(base_dir),wordcloud,str(id))
        self.curs.execute(update_wordcloud_path)
        self.conn.commit()
        pass