# encoding:utf-8
import config as cfg
import requests
from lxml import etree
import ssl
from functools import wraps
try:
    from urllib.request import Request,urlopen,ProxyHandler,build_opener,install_opener  # Python 3
except ImportError:
    from urllib2 import Request,urlopen,ProxyHandler,build_opener,install_opener  # Python 2

def test1():
    #### 测试——律金刚 222.89.32.160:9999  61.128.208.94:3128 114.134.190.230:40636 95.174.109.43:36804 210.26.64.44:3128 61.128.208.94:3128 
    ## 134.119.205.163:8080 181.191.85.114:8080 122.55.48.131:8080 203.128.71.178:8080 114.134.190.230:40636 1.20.102.68:8080 110.74.208.154:21776
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    url = "https://ip.cn"
    ip = "182.61.175.77:8118"
    #proxy = {"http": "http://"+ip,"https": "https://"+ip}
    #proxy = {"http": "http://"+ip}
    proxy = {"https": "https://"+ip}
    ##r = requests.get("http://app.ljgchina.com/p/login_xjh?token=dd9ff490901e1dbf3128151da1c17e70")
    ## http://httpbin.org/get  https://www.baidu.com  http://icanhazip.com  http://ip.tool.chinaz.com/  https://ip.cn  https://support.google.com  http://www.882667.com  http://www.ip168.com/
    requests.packages.urllib3.disable_warnings()
    r = requests.get(url,proxies=proxy,headers=headers,timeout=30,verify=False)
    print (r.text)
    print (r.status_code)
    r.close()
    
def test2():
    ip = "111.11.98.58:9000"
    proxy = ProxyHandler({'http': 'http://'+ip+'/','https': 'http://'+ip})
    # 代理ip需要用户名密码验证
    #auth = HTTPBasicAuthHandler()
    #auth.add_password("realm","host","username","password")
    #opener = build_opener(proxy,auth)
    opener = build_opener(proxy)
    #install_opener(opener)
    # 关闭SSL证书认证，用于访问https://
    ssl._create_default_https_context = ssl._create_unverified_context
    r = opener.open("http://ip.cn/",timeout=20)
    print (r.readlines())
    print ('----')
    #print (r.fileno())
    print (r.info())
    print ('----')
    print (r.getcode())
    print ('----')
    print (r.geturl())
    r.close()
    
if __name__ == '__main__':
    test1()

#url = "https://www.12306.cn/mormhweb/" 
#headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36", 'Connection': 'keep-alive'} 
#request = urllib2.Request(url, headers = headers)
# 忽略未经核实的SSL证书认证
#context = ssl._create_unverified_context()
# 在urlopen()方法里 指明添加 context 参数
#response = urllib2.urlopen(request, context=context)

# 强制ssl使用TLSv1  
#def sslwrap(func):  
#    @wraps(func)  
#    def bar(*args, **kw):  
#        kw['ssl_version'] = ssl.PROTOCOL_TLSv1  
#        return func(*args, **kw)  
#    return bar  
#ssl.wrap_socket = sslwrap(ssl.wrap_socket)
