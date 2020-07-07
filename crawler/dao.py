import re
from threading import Thread
import pymysql
from datetime import datetime

class DAO:
    def __init__(self, host='103.55.190.32', port=3306,  user='wordcloud', password='word6244!@', db='crawl', charset='utf8mb4'):

        self.conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db,
                               charset=charset)
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.close = self.conn.close

    def check_process(self,server_name):
        sql_check_process = "select * from multi_process where server_name=\'%s\'" % (server_name)
        self.curs.execute(sql_check_process)
        rows_process = self.curs.fetchall()
        return rows_process[0]

    def select_gr(self):
        sql_gr = "select * from polls_breakdown where status=\'%s\' order by create_time  " % ('GR')
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
        rows_proxy = self.curs.fetchall()
        return rows_proxy
    def select_available_proxy(self,server='ydns'):
        select_check_proxy = "select * from server_proxy where server=\'%s\' and status=\'%s\'" % (server, 'P')
        self.curs.execute(select_check_proxy)
        rows_proxy = self.curs.fetchall()
        return rows_proxy

    def select_proxy(self,proxy_id):
        select_proxy = "select * from server_proxy where id=%s" % (proxy_id)
        self.curs.execute(select_proxy)
        rows_proxy = self.curs.fetchall()
        return rows_proxy

    def select_sever_proxy(self,server='ydns'):
        select_check_proxy = "select * from server_proxy where server=\'%s\'" % (server)
        self.curs.execute(select_check_proxy)
        selected_proxy_rows = self.curs.fetchall()
        return selected_proxy_rows

    def select_total_proxy(self):
        select_total_proxy = "select * from server_proxy"
        self.curs.execute(select_total_proxy)
        total_proxy_rows = self.curs.fetchall()
        return total_proxy_rows

    def update_process_IN(self,server_name):
        sql_update_process_in = "update multi_process set status=\'%s\' where server_name =\'%s\'"%('IN',server_name)
        self.curs.execute(sql_update_process_in)
        self.conn.commit()

    def update_process_OUT(self,server_name):
        sql_update_process_out = "update multi_process set status=\'%s\' where server_name =\'%s\'"%('OUT',server_name)
        self.curs.execute(sql_update_process_out)
        self.conn.commit()

    def update_gi(self,id):
        sql_update_gi = "update polls_breakdown set status=\'%s\' where id =\'%s\'"%('GI',id)
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