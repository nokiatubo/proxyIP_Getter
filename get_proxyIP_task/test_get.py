# coding:utf-8
import time
import config as cfg
import requests
from lxml import etree
import pymysql as mdb
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
#import ssl
#from functools import wraps

##
## 使用Python 2 运行
##
class IPGetter:
    """
    代理ip，抓取 -> 评估 -> 存储一体化
    """
    def __init__(self):
        self.page_num = cfg.page_num
        self.round = cfg.examine_round
        self.round_time = cfg.round_time
        self.get_timeout = cfg.get_timeout
        self.interval_time = cfg.interval_time
        self.url_http = cfg.url_http
        self.url_https = cfg.url_https
        self.headers = cfg.headers
        self.timeout = cfg.timeout
        self.all_ip = set()

        requests.adapters.DEFAULT_RETRIES = 5
        ## 屏蔽ssl连接告警
        requests.packages.urllib3.disable_warnings()

        #连接数据库
        self.conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.DB_NAME)
        self.cursor = self.conn.cursor()
        
        # 创建数据库
        #self.create_db()

        # # 抓取全部ip
        # current_ips = self.get_all_ip()
        # # 获取有效ip
        # valid_ip = self.get_the_best(current_ips, self.timeout, self.round)
        # print valid_ip

    def create_db(self):
        """
        创建数据库用于保存有效ip
        """
        # 创建数据库/表语句
        # 新建数据库
        drop_db_str = 'drop database if exists ' + cfg.DB_NAME + ' ;'
        create_db_str = 'create database ' + cfg.DB_NAME + ' ;'
        # 选择该数据库
        use_db_str = 'use ' + cfg.DB_NAME + ' ;'
        # 新建数据表
        create_table_str = "CREATE TABLE " + cfg.TABLE_NAME + """(
          `content` varchar(30) NOT NULL COMMENT 'IP:port',
          `is_http` tinyint(3) DEFAULT NULL COMMENT 'http代理',
          `is_https` tinyint(3) DEFAULT NULL COMMENT 'https代理',
          `test_times` int(5) NOT NULL DEFAULT '0' COMMENT '测试次数',
          `failure_times` int(5) NOT NULL DEFAULT '0' COMMENT '失败次数',
          `success_rate` float(5,2) NOT NULL DEFAULT '0.00' COMMENT '成功率',
          `avg_response_time` float NOT NULL DEFAULT '0' COMMENT '平均响应时间',
          `score` float(5,2) NOT NULL DEFAULT '0.00' COMMENT '分数',
          `lastchecktime` datetime DEFAULT NULL COMMENT '最后检查时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        # 连接数据库
        conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd)
        cursor = conn.cursor()
        try:
            cursor.execute(drop_db_str)
            cursor.execute(create_db_str)
            cursor.execute(use_db_str)
            cursor.execute(create_table_str)
            conn.commit()
        except OSError:
            print u"无法创建数据库！"
        finally:
            cursor.close()
            conn.close()

    def get_all_ip(self):
        """
        抓取各大代理网站的ip
        """
        # 有2个概念：all_ip和current_all_ip。前者保存了历次抓取的ip，后者只保存本次的抓取。
        current_all_ip = set()

        ##################################
        # 66ip
        ###################################
        ip_xpath_66 = '/html/body/div["main"]//table//tr[position()>1]/td[1]/text()'
        port_xpath_66 = '/html/body/div[last()-2]//table//tr[position()>1]/td[2]/text()'
        for i in xrange(self.page_num):
            url_66 = 'http://www.66ip.cn/' + str(i+1) + '.html'
            results = self.get_content(url_66, ip_xpath_66, port_xpath_66)
            self.all_ip.update(results)
            current_all_ip.update(results)
            # 停0.5s再抓取
            time.sleep(self.interval_time)

        ##################################
        # xici代理
        ###################################
        ip_xpath_xici = '//table[@id="ip_list"]//tr[position()>1]/td[position()=2]/text()'
        port_xpath_xici = '//table[@id="ip_list"]//tr[position()>1]/td[position()=3]/text()'
        for i in xrange(self.page_num):
            url_xici = 'http://www.xicidaili.com/nn/' + str(i+1)
            results = self.get_content(url_xici, ip_xpath_xici, port_xpath_xici)
            self.all_ip.update(results)
            current_all_ip.update(results)
            time.sleep(self.interval_time)

        ##################################
        # mimiip
        ###################################
        # ip_xpath_mimi = '//table[@class="list"]//tr[position()>1]/td[1]/text()'
        # port_xpath_mimi = '//table[@class="list"]//tr[position()>1]/td[2]/text()'
        # for i in xrange(self.page_num):
        #     url_mimi = 'http://www.mimiip.com/gngao/' + str(i+1)
        #     results = self.get_content(url_mimi, ip_xpath_mimi, port_xpath_mimi)
        #     self.all_ip.update(results)
        #     current_all_ip.update(results)
        #     time.sleep(0.5)

        ##################################
        # kuaidaili
        ###################################
        ip_xpath_kuaidaili = '//td[@data-title="IP"]/text()'
        port_xpath_kuaidaili = '//td[@data-title="PORT"]/text()'
        for i in xrange(self.page_num):
            url_kuaidaili = 'http://www.kuaidaili.com/free/inha/' + str(i+1) + '/'
            results = self.get_content(url_kuaidaili, ip_xpath_kuaidaili, port_xpath_kuaidaili)
            self.all_ip.update(results)
            current_all_ip.update(results)
            time.sleep(self.interval_time)

        return current_all_ip

    def get_content(self, url, ip_xpath, port_xpath):
        """
        使用xpath解析网页内容,并返回ip:port列表。
        """
        # 返回列表
        ip_list = []

        try:

            # 获取页面数据
            results = requests.get(url, headers=self.headers, timeout=self.get_timeout)
            tree = etree.HTML(results.text)

            # 提取ip:port
            ip_results = tree.xpath(ip_xpath)
            port_results = tree.xpath(port_xpath)
            ips = [line.strip() for line in ip_results]
            ports = [line.strip() for line in port_results]

            if len(ips) == len(ports):
                for i in range(len(ips)):
                    # 匹配ip:port对
                    full_ip = ips[i]+":"+ports[i]
                    # 此处利用all_ip对过往爬取的ip做了记录，下次再爬时如果发现已经爬过，就不再加入ip列表。
                    if full_ip in self.all_ip:
                        continue
                    # 存储
                    ip_list.append(full_ip)
        except Exception as e:
            print 'get error: ', e
        except requests.ReadTimeout:
            print 'failed: ' + self.url + u' 加载超时！'
            
        return ip_list

    def get_the_best(self, valid_ip, timeout, round):
        """
        N轮检测ip列表，避免"辉煌的15分钟"
        """
        # 循环检查次数
        for i in range(round):
            print u"\n>>>>>>>\t第\t"+str(i+1)+u"\t轮<<<<<<<<<<"
            # 检查代理是否可用
            valid_ip = self.get_valid_ip(valid_ip, timeout)
            # 停一下
            if i < round-1:
                time.sleep(self.round_time)

        return valid_ip

    def get_valid_ip(self, ip_set, timeout):
        """
        代理ip可用性测试
        """
        # 设置可用代理ip结果集
        results = set()
        if self.conn is None:
            self.conn = mdb.connect(host=cfg.host, port=cfg.port, user=cfg.user, passwd=cfg.passwd, db=cfg.DB_NAME)
            self.cursor = self.conn.cursor()
        ishttp = None
        time1 = None
        ishttps = None
        time2 = None
        # 逐个检查代理ip是否可用，协议类型
        for ip in ip_set:
            #proxy = {'http':'http://'+ip, 'https':'http://'+ip}
            try:
                proxy_http = {'http':'http://'+ip}
                # 请求开始时间
                start1 = time.time()
                r = requests.get(self.url_http, proxies=proxy_http, headers=self.headers, timeout=timeout, verify=False)
                # 请求结束时间
                end1 = time.time()
                # 判断是否可用
                ##if r.text is not None:
                if r.status_code == 200:
                    ishttp = 1
                    time1 = end1-start1
                    print 'succeed: ' + ip + '\t' + "tested for Http in " + format(time1, '0.3f') + 's'
                else:
                    ishttp = 0
                    time1 = 0
            except requests.ConnectTimeout:
                ishttp = 0
                time1 = 0
                print 'failed: ' + ip + u' 连接Http代理超时！'
            except requests.ConnectionError as e:
                ishttp = 0
                time1 = 0
                print 'failed: ' + ip + u' ConnectionError！' + str(e)
            except requests.Timeout:
                ishttp = 0
                time1 = 0
                print 'failed: ' + ip + u' 请求URL超时！'
            except requests.HTTPError:
                ishttp = 0
                time1 = 0
                print 'failed: ' + ip + u' HTTP错误异常！'
            except requests.ReadTimeout:
                ishttp = 0
                time1 = 0
                print 'failed: ' + self.url_http + u' 加载超时！'

            try:
                proxy_https = {'https':'http://'+ip}
                # 请求开始时间
                start2 = time.time()
                r = requests.get(self.url_https, proxies=proxy_https, headers=self.headers, timeout=timeout, verify=False)
                # 请求结束时间
                end2 = time.time()
                # 判断是否可用
                ##if r.text is not None:
                if r.status_code == 200:
                    ishttps = 1
                    time2 = end2-start2
                    print 'succeed: ' + ip + '\t' + "tested for HTTPS in " + format(time2, '0.3f') + 's'
                else:
                    ishttps = 0
                    time2 = 0
            except requests.ConnectTimeout:
                ishttps = 0
                time2 = 0
                print 'failed: ' + ip + u' 连接HTTPS代理超时！'
            except requests.ConnectionError as e:
                ishttps = 0
                time2 = 0
                print 'failed: ' + ip + u' ConnectionError！' + str(e)
            except requests.Timeout:
                ishttps = 0
                time2 = 0
                print 'failed: ' + ip + u' 请求URL超时！'
            except requests.HTTPError:
                ishttps = 0
                time2 = 0
                print 'failed: ' + ip + u' HTTP错误异常！'
            except requests.ReadTimeout:
                ishttps = 0
                time2 = 0
                print 'failed: ' + self.url_https + u' 加载超时！'
            # 追加代理ip到返回的结果集中，同时写入数据库
            if ishttp | ishttps:
                results.add(ip)
                if ishttp & ishttps:
                    self.save_to_db(ip,ishttp,ishttps,(time1+time2)/2)
                else:
                    self.save_to_db(ip,ishttp,ishttps,(time1+time2))
        self.cursor.close()
        self.conn.close()
        return results

    def save_to_db(self, ip, ishttp, ishttps, response_time):
        """
        将可用的ip存储进mysql数据库
        """
        #print u"\n>>>>>>>>>>>>>>>>>>>> 代理数据入库处理_Start <<<<<<<<<<<<<<<<<<<<<<"
        try:
            if not response_time:
                response_time=1.0
            # 检查表中是否存在数据
            item_exist = self.cursor.execute('SELECT * FROM %s WHERE content="%s"' %(cfg.TABLE_NAME, ip))
            # 代理ip入库
            if item_exist == 0:
                # 插入代理ip
                n = self.cursor.execute('INSERT INTO %s VALUES("%s", %d, %d, 1, 0, 1.0, "%0.3f", 2.5, "%s")'%(cfg.TABLE_NAME,ip,ishttp,ishttps,response_time,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.conn.commit()
                # 输出入库状态
                if n:
                    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": "+ip +u" 插入成功。"
                else:
                    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": "+ip +u" 插入失败？"
            else:
                print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": "+ ip +u" 已存在！"
        except Exception as e:
            print u"入库失败：" + str(e)
        finally:
            pass
            #cursor.close()
            #conn.close()
        #print u">>>>>>>>>>>>>>>>>>>> 代理数据入库处理_End <<<<<<<<<<<<<<<<<<<<<<"

    def get_proxies(self):
        ip_list = []
        # 连接数据库
        conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
        cursor = conn.cursor()
        # 检查数据表中是否有数据
        try:
            ip_exist = cursor.execute('SELECT * FROM %s ' % cfg.TABLE_NAME)

            # 提取数据
            result = cursor.fetchall()

            # 若表里有数据　直接返回，没有则抓取再返回
            if len(result):
                for item in result:
                    ip_list.append(item[0])
            else:
                # 获取代理ip
                current_ips = self.get_all_ip()
                valid_ips = self.get_the_best(current_ips, self.timeout, self.round)
                self.save_to_db(valid_ips)
                ip_list.extend(valid_ips)
        except Exception as e:
            print u"从数据库获取ip失败！"
        finally:
            cursor.close()
            conn.close()
        return ip_list

def main():
    ip_pool = IPGetter()
    while True:
        current_ips = ip_pool.get_all_ip()
        ##current_ips = ['218.91.94.11:9999', '49.89.220.106:9999', '1.197.203.196:9999', '112.85.168.249:9999']
        # 获取有效ip
        valid_ip = ip_pool.get_the_best(current_ips, cfg.timeout, cfg.examine_round)
        print valid_ip
        print(u'本次新增代理IP数： '+str(len(valid_ip)))
        time.sleep(cfg.CHECK_TIME_INTERVAL)

def test_db(ip,ishttp,ishttps, response_time):
    start = time.time()
    test = IPGetter()
    end = time.time()
    test.save_to_db(ip,ishttp,ishttps, (end-start))
    test.cursor.close()
    test.conn.close()

def test_getip():
    ## 66ip
    ip_xpath = '/html/body/div[@id="main"]//table//tr[position()>1]/td[1]/text()'
    port_xpath = '/html/body/div[last()-2]//table//tr[position()>1]/td[2]/text()'
    url = 'http://www.66ip.cn/' + "1" + '.html'
    ## xicidaili
    #ip_xpath = '//table[@id="ip_list"]//tr[position()>1]/td[position()=2]/text()'
    #port_xpath = '//table[@id="ip_list"]//tr[position()>1]/td[position()=3]/text()'
    #url = 'http://www.xicidaili.com/nn/' + "1"
    ## kuaidaili
    #ip_xpath = '//td[@data-title="IP"]/text()'
    #port_xpath = '//td[@data-title="PORT"]/text()'
    #url = 'http://www.kuaidaili.com/free/inha/' + "1" + '/'
    ## http://www.goubanjia.com/
    #ip_xpath = '//tr[position()>1]/td[1]/text()'
    #port_xpath = ''
    #url = "http://www.goubanjia.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko'}
    results = requests.get(url, headers=headers, timeout=4)
    print "results.text: "+results.text
    tree = etree.HTML(results.text)
    print tree
    #print "tree: "+etree.tostring(results.text).decode()
    ip_results = tree.xpath(ip_xpath)
    print ip_results
    port_results = tree.xpath(port_xpath)
    print port_results
    ips = [line.strip() for line in ip_results]
    print ips
    ports = [line.strip() for line in port_results]
    print ports
    if len(ips) == len(ports):
        for i in range(len(ips)):
            full_ip = ips[i]+":"+ports[i]
            print "full_ip: "+full_ip

if __name__ == '__main__':
    main()

    #test_db(['0.0.0.1:1'],1,1,0.5)
    
    # 测试抓取网站IP
    #test_getip()

    #### 测试IP
    #ipset = ['222.89.32.160:9999', '49.89.220.106:9999', '112.85.168.249:9999', '1.197.203.196:9999']
    #iptest = IPGetter()
    #valid_ip = iptest.get_the_best(ipset,IPGetter().timeout,IPGetter().round)
    #print valid_ip

    #### 测试——律金刚
    #ip = "222.89.32.160:9999"
    #proxy = {'http':'http://'+ip}
    #proxy = {'https':'http://'+ip}
    #proxy = {"http":"http://"+ip,"https":"https://"+ip}
    #requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    ##requests.packages.urllib3.disable_warnings()
    ##r = requests.get("http://app.ljgchina.com/p/login_xjh?token=dd9ff490901e1dbf3128151da1c17e70")
    ## http://httpbin.org/get  https://www.baidu.com  http://www.baidu.com
    #r = requests.get("https://www.baidu.com",proxies=proxy,timeout=5,verify=False)
    #print r.text
    #print r.status_code
