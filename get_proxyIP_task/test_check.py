#!/user/bin/env python
# -*- coding:utf-8 -*-
##
## 使用Python 2 运行
##

import requests
import time
import datetime
import logging
import pymysql as mdb
import config as cfg
import os

class IPChecker:
    def __init__(self):
        self.log_file = 'logs\check_logger_'+datetime.datetime.now().strftime("%Y-%m-%d")+'.log'
        if not os.path.exists(self.log_file):
            f = open(self.log_file,'w')
            f.close()
        logging.basicConfig(filename=self.log_file, level=logging.INFO)
        self.TEST_ROUND_COUNT = 0

        requests.adapters.DEFAULT_RETRIES = 5
        ## 屏蔽ssl连接告警
        requests.packages.urllib3.disable_warnings()
        
        #连接数据库
        self.conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.DB_NAME)
        self.cursor = self.conn.cursor()

    def access(self):
        '''
        访问数据库，获取所有代理IP -> 检查代理ip可用性 -> 评分
        '''
        self.TEST_ROUND_COUNT
        self.TEST_ROUND_COUNT += 1
        logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + u">>>>第\t" + str(self.TEST_ROUND_COUNT) + u"\t轮!<<<<")
        try:
            if self.conn is None:
                self.conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.DB_NAME)
                self.cursor = self.conn.cursor()
            self.cursor.execute('SELECT content,is_http,is_https FROM %s' % cfg.TABLE_NAME)
            result = self.cursor.fetchall()
            if len(result) == 0:
                return
            self.ip_test(result, cfg.timeout)
        except Exception as e:
            print(":access: " + str(e))
            logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+u":access: " + str(e))
        finally:
            self.cursor.close()
            self.conn.close()

    def ip_test(self, ips, timeout):
        ''''
        检查代理ip可用性
        '''
        ishttp = None
        time1 = None
        ishttps = None
        time2 = None
        for ip,http,https in ips:
            #proxy = {'http':'http://'+ip, 'https':'https://'+ip}
            try:
                proxy_http = {'http':'http://'+ip}
                # 请求开始时间
                start1 = time.time()
                r = requests.get(cfg.url_http, proxies=proxy_http, headers=cfg.headers, timeout=timeout)
                # 请求结束时间
                end1 = time.time()
                # 判断是否可用
                ##if r.text is not None:
                if r.status_code == 200:
                    ishttp=1
                    time1 = end1 -start1
                    print u'代理ip测试成功： '+ip+'\tfor Http in '+str(time1) + 's'
                    logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + u" 测试成功！for Http in "+str(time1) + 's')
                else:
                    ishttp=0
                    time1=0
            except requests.ConnectTimeout:
                ishttp=0
                time1=0
                print 'failed: ' + ip + u' 连接Http代理超时！'
            except requests.ConnectionError as e:
                ishttp=0
                time1=0
                print 'failed: ' + ip + u' ConnectionError！' + str(e)
            except requests.Timeout:
                ishttp=0
                time1=0
                print 'failed: ' + ip + u' 请求URL超时！'
            except requests.HTTPError:
                ishttp=0
                time1=0
                print 'failed: ' + ip + u' HTTP错误异常！'
            except requests.exceptions.ProxyError as e:
                ishttp=0
                time1=0
                print 'failed: ' + ip + u' ProxyError！' + str(e)
            except requests.ReadTimeout as e:
                ishttp=0
                time1=0
                print 'failed: ' + self.url_http + u' 加载超时！'
                #logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+u":ip_test.ReadTimeout: " + str(e))
            except Exception as e:
                ishttp=0
                time1=0
                print("ip_test_Http: "+ ip + str(e))
                logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+u":ip_test_Http: " + str(e))

            try:
                proxy_https = {'https':'http://'+ip}
                # 请求开始时间
                start2 = time.time()
                r = requests.get(cfg.url_https, proxies=proxy_https, headers=cfg.headers, timeout=timeout, verify=False)
                # 请求结束时间
                end2 = time.time()
                # 判断是否可用
                ##if r.text is not None:
                if r.status_code == 200:
                    ishttps=1
                    time2 = end2 -start2
                    print u'代理ip测试成功： '+ip+'\tfor HTTPS in '+str(time2) + 's'
                    logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + u" 测试成功！for HTTPS in "+str(time2) + 's')
                else:
                    ishttps=0
                    time2=0
            except requests.ConnectTimeout:
                ishttps=0
                time2=0
                print 'failed: ' + ip + u' 连接HTTPS代理超时！'
            except requests.ConnectionError as e:
                ishttps=0
                time2=0
                print 'failed: ' + ip + u' ConnectionError！' + str(e)
            except requests.Timeout:
                ishttps=0
                time2=0
                print 'failed: ' + ip + u' 请求URL超时！'
            except requests.HTTPError:
                ishttps=0
                time2=0
                print 'failed: ' + ip + u' HTTP错误异常！'
            except requests.exceptions.ProxyError as e:
                ishttps=0
                time2=0
                print 'failed: ' + ip + u' ProxyError！' + str(e)
            except requests.ReadTimeout as e:
                ishttps=0
                time2=0
                print 'failed: ' + self.url_https + u' 加载超时！'
                #logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+u":ip_test.ReadTimeout: " + str(e))
            except Exception as e:
                ishttps=0
                time2=0
                print("ip_test_HTTPS: "+ ip + str(e))
                logging.warning(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+u":ip_test_HTTPS: " + str(e))
            
            if ishttp | ishttps:
                if ishttp & ishttps:
                    self.modify_score(ip, ishttp, ishttps, 1, (time1+time2)/2)
                else:
                    self.modify_score(ip, ishttp, ishttps, 1, (time1+time2))
            else:
                self.modify_score(ip, http, https, 0, 0)
                
    def modify_score(self, ip, ishttp, ishttps, success, response_time):
        '''
        代理ip评分，success == 0 表示代理ip测试失败
        '''
        # 连接数据库
        if self.conn is None:
            self.conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.DB_NAME)
            self.cursor = self.conn.cursor()
        # 代理ip超时
        if success == 0:
            try:
                self.cursor.execute('SELECT * FROM %s WHERE content= "%s"' % (cfg.TABLE_NAME, ip))
                q_result = self.cursor.fetchall()
                for r in q_result:
                    # 测试次数
                    test_times = r[3] + 1
                    # 失败次数
                    failure_times = r[4] + 1
                    # 成功率
                    success_rate = r[5]
                    # 响应时间
                    avg_response_time = r[6]
                    # 超时次数达到且成功率低于配置值，则从数据库中删除
                    if failure_times > cfg.FAILURE_TIME and success_rate < cfg.SUCCESS_RATE:
                        self.cursor.execute('DELETE FROM %s WHERE content= "%s"' % (cfg.TABLE_NAME, ip))
                        self.conn.commit()
                        logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + u" 已删除！")
                    else:
                        success_rate = 1 - float(failure_times) / test_times
                        avg_response_time = (avg_response_time * (test_times - 1) + response_time + cfg.TIME_OUT_PENALTY) / test_times
                        #score = (success_rate + float(test_times) / 500) / avg_response_time
                        score = success_rate * float(test_times) / avg_response_time
                        n = self.cursor.execute('UPDATE %s SET is_http=%d, is_https=%d, test_times=%d, failure_times=%d, success_rate=%.2f, avg_response_time=%.2f, score=%.2f, lastchecktime="%s" WHERE content= "%s"' % \
                                           (cfg.TABLE_NAME, ishttp, ishttps, test_times, failure_times, success_rate, avg_response_time, score, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip))
                        self.conn.commit()
                        if n:
                            print(ip + u' 超时，数据更新！')
                            logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + u' 异常，数据更新！')
                    break
            except Exception as e:
                print("success=0: " + ip + str(e))
                logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+":success=0: " + ip + str(e))
            finally:
                pass
        # 代理ip测试成功
        elif success == 1:
            try:
                self.cursor.execute('SELECT * FROM %s WHERE content= "%s"' % (cfg.TABLE_NAME, ip))
                q_result = self.cursor.fetchall()
                for r in q_result:
                    test_times = r[3] + 1
                    failure_times = r[4]
                    success_rate = r[5]
                    avg_response_time = r[6]
                    success_rate = 1 - float(failure_times) / test_times
                    avg_response_time = (avg_response_time * (test_times - 1) + response_time) / test_times
                    #score = (success_rate + float(test_times) / 500) / avg_response_time
                    score = success_rate * float(test_times) / avg_response_time
                    n = self.cursor.execute('UPDATE %s SET is_http=%d, is_https=%d, test_times = %d, success_rate = %.2f, avg_response_time = %.2f, score = %.2f, lastchecktime="%s" WHERE content = "%s"' % \
                                       (cfg.TABLE_NAME, ishttp, ishttps, test_times, success_rate, avg_response_time, score, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip))
                    self.conn.commit()
                    if n:
                        print(ip + u' 数据已更新！')
                        logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": " + ip + u' 数据已更新！')
                    break
            except Exception as e:
                print("success=1: " + ip + str(e))
                logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':success=1: ' + ip + str(e))
            finally:
                pass

def main():
    checker = IPChecker()
    while True:
        checker.access()
        # 定时执行
        time.sleep(cfg.CHECK_TIME_INTERVAL)

if __name__ == '__main__':
    main()
    #print "null"
