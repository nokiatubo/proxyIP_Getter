# encoding:utf-8
# 从代理ip网站上总共要爬取的页数。一般每页20条，小项目可以设置为1-2页
page_num = 3
# 爬取每一页的间隔时间，单位：秒
interval_time = 0.5
# 获取代理ip网站页面数据的超时时间，单位：秒
get_timeout = 5
# 对抓取到的ip进行有效性测试的轮次
examine_round = 1
# 每一轮的间隔时间，单位：秒
round_time = 300
# 代理ip可用性测试地址
# http://httpbin.org/get http://icanhazip.com http://ip.tool.chinaz.com
# http://www.882667.com http://www.ip168.com
# https://www.baidu.com https://ip.cn
url_https = "https://ip.cn"
url_http = "http://www.ip168.com"
# 网页headers请求头信息
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
#headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36", 'Connection': 'keep-alive'} 
# 代理ip在测试过程中的超时时间，单位：秒
timeout = 10
# 数据库地址
host = 'localhost'
# 数据库端口
port = 3306
# 数据库用户名
user = 'root'
# 数据库密码
passwd = 'root'
# 数据库名
DB_NAME = 'proxy'
# 表名
TABLE_NAME = 'valid_ip'
# 数据库字符
charset = 'utf8'
# 1个代理ip最大容忍失败次数，达到则从db中删去
FAILURE_TIME = 10
# 1个代理ip最小容忍成功率，超过则从db中删去
SUCCESS_RATE = 0.1
# 超时惩罚时间，单位：秒。建议同timeout
TIME_OUT_PENALTY = 5
# 每隔多久检测一次
CHECK_TIME_INTERVAL = 24*3600
