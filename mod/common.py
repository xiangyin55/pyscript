# -*- encoding: utf-8 -*-

import threading
import requests,urllib
import json,time,re,random,datetime

import mod.logger as logger


log = logger.logger()

def threadrun(func,ids,tcount):
    threads = []
    task = {}
    if not ids : return
    tcount = tcount if len(ids)> tcount else len(ids)
    i = 0
    for id in ids:
        mod = i % tcount
        if (mod not in task): task[mod] = []
        task[mod].append(id)
        i = i + 1



    for i in range(len(task)):
        t = threading.Thread(target=func,args=(task[i],i))
        threads.append(t)

    for i in range(len(task)):
        threads[i].start()

    for i in range(len(task)):
        threads[i].join()

    log.info ('Multi threading tasks ' + str(func) + ' is over!!')


def craw(url,params=None,headers=None,method='get'):
    agents =[
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
        ]

    headers = headers if headers else {'User-Agent':random.choice(agents)}

    if not url[0:4].lower() == 'http':
        url = 'http://'+ url


    try:
        #requests.session().keep_alive=False
        #requests.adapters.DEFAULT_RETRIES = 1
        #requests.adapters.DEFAULT_RETRIES =1   # 增加重连次数
        #s = requests.session()
        #s.keep_alive = False   # 关闭多余连接
        #s.headers= headers
        #s.get(url)# 你需要的网址
        if method == 'post':
            response = requests.post(url,data=params,headers=headers,timeout=1)
        else:
            response = requests.get(url,params,headers=headers)
        if response.status_code == requests.codes.ok :
            return response
        elif response.status_code == 403:
            log.critical ('Request Error 403')
            exit('403')
        elif response.status_code == 404:
            log.critical ('Request Error 404')
            exit('404')
        else:
            log.warning (response.status_code)
            log.warning (response.url)
            time.sleep(random.randint(0,1))

    except Exception as e:
        log.warning (e)

    return

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


if __name__ == '__main__':
    #a = craw('a.bc.cn')

    getch = _Getch()
    a = getch()
    if(a == "3"):
      print("yes")
    else:
      print("no")


