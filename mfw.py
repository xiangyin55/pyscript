#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      Administrator
#
# Created:     28/04/2019
# Copyright:   (c) Administrator 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import threading
import requests
import json,time,re,random
import sqlite3
import js2py
from pyquery import PyQuery as pq
import mod.db as db
import winsound

jm = js2py.eval_js(open("mfw.js",'r').read())
ld = True




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

    print ('Multi threading tasks ' + str(func) + ' is over!!')


def craw(url,params=None,headers=None,method='get'):

    headers = headers if headers else {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    #print (url)

    try:
        if method == 'post':
            response = requests.post(url,data=params,headers=headers)
        else:
            response = requests.get(url,params,headers=headers)
        if response.status_code == requests.codes.ok :
            return response
        elif response.status_code == 403:
            print ('Request Error 403')
            exit('403')
        else:
            print (response.status_code)
            print (response.url)

    except Exception as e:
        print (response.url)
        print (e)

    return

def province():

    response = craw('http://z.mafengwo.cn/jd')

    if not response : return

    ss = []
    listdoc = pq(response.text)('.hot_city > .clearfix')

    for each in listdoc('a[href^="http://z.mafengwo.cn/jd/"]').items():
        if each.attr.href == response.url : continue
        o = {}
        o['id'] = each.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = ''
        o['level'] = 1
        o['name'] = each.text().split(u"（")[0].replace('"','').replace("'",'')
        ss.append(o)
        #if ld : print (json.dumps(o,ensure_ascii = False))

    return ss

def _city(response,mddid):
    ids = []
    if response == None : return

    ldoc = pq(response.json()["list"])
    for d in ldoc('a').items():
        if 'travel-scenic-spot' in d.attr.href:
            o = {}
            o['id'] = d.attr.href.split("/")[-1].split(".")[0]
            o['parent'] = mddid
            o['level'] = 2
            o['name'] = d.text().split("\n")[0]
            ids.append(o)


    pdoc = pq(response.json()["page"])  #print (page_doc.html())
    if  pdoc(".pg-next"):
        url = 'https://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        ipage = pdoc(".pg-next").attr("data-page")
        params = {'mddid': mddid, 'page': ipage }
        params = json.loads( jm( json.dumps(params)))
        rs = craw(url,params,method='post')
        ids = ids + _city(rs,mddid)

    return ids

def citys(mdds):
    if not mdds : return

    for m in mdds:
        time.sleep(random.randint(1,2))
        cs = []
        url = 'https://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        params = {'mddid': m[0], 'page': 1}
        params = json.loads( jm( json.dumps(params)))
        response = craw(url,params,method='post')
        cs = _city(response,m[0])
        db.t_mdd_a(cs)
        print (len(cs))


def _aoi(response,mddid):

    ids = []

    if response == None : return
    j = response.json()
    if 'data' not in j : return
    j = j['data']

    if j["list"] :
        ldoc = pq(j["list"])
        for d in ldoc('a').items():
            o = {}
            o['id'] = d.attr.href.split("/")[-1].split(".")[0]
            o['parent'] = ''
            o['mdd'] = mddid
            o['level'] = '3'
            o['name'] = d.text().split("\n")[0]
            ids.append(o)



    if j["page"]:
        pdoc = pq(j["page"])  #print (page_doc.html())
        if  pdoc(".pg-next"):
            ipage = pdoc(".pg-next").attr("data-page")
            url ='https://www.mafengwo.cn/ajax/router.php'
            params = {
            'iMddid' : mddid,
            'iPage': ipage,
            'iTagId': '0',
            'sAct': 'KMdd_StructWebAjax|GetPoisByTag'
            }
            params = json.loads( jm( json.dumps(params) ) )
            rs = craw(url,params)
            ids = ids + _aoi(rs,mddid)

    return ids

def aois(ids,tid):
    if not ids : return
    i = 0
    for m in ids:
        time.sleep(random.randint(1,10))
        cs = []
        url ='https://www.mafengwo.cn/ajax/router.php'
        params = {
        'iMddid' : m[0],
        'iPage': 1,
        'iTagId': '0',
        'sAct': 'KMdd_StructWebAjax|GetPoisByTag'
        }
        params = json.loads( jm( json.dumps(params) ) )

        response = craw(url,params)
        cs = _aoi(response,m[0])
        if (cs == []):
            db.t_mdd_u(m[0])
        else:
            db.t_poi_a(cs)
        i = i + 1
        print ("threads-{0}: no {1}. process {2} , finished, fond {3} records ".format(tid,str(i),m[0], str(len(cs))))



def _poi(poiid,response):

    if not response : return

    if 'html' not in response.json()['data'] : return
    if  not  response.json()['data']['html'] : return

    ids = []

    ldoc = pq(response.json()['data']['html'])
    control = response.json()['data']['controller_data']
    #print (control)

    for d in ldoc('a[href^="/poi"]').items():
        go = d.find('em').text()
        o = {}
        o['id'] = d.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = control['poi_id']
        o['mdd'] = ''
        o['level'] = 4
        o['name'] = d.attr.title
        #print (o)
        ids.append(o)


    if control['hasMore'] :
        page = control['curPage'] + 1
        poi = control['poi_id']
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+str(poi)+'","type":3,"page":'+str(page)+'}'
        s = _poi(poi,craw(url))
        ids = ids + s
    return ids



def pois(ids,tid):
    if not ids : return
    i = 0
    for m in ids:
        time.sleep(random.randint(1,10))
        cs = []
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+m[0]+'","type":3,"page":1}'
        response = craw(url)
        ps = _poi(m[0],response)
        if (ps == []):
            db.t_poi_u(m[0])
        else:
            db.t_poi_a(ps)

        i = i + 1
        leng = str(len(ps)) if not ps == None else '0'
        mlen = str(len(ids))
        print ("threads-{0}: no {1}/{2}. process {3} , finished, fond {4} records ".format(tid, str(i), mlen, m[0], leng))



def poisloc(ids,tid=1):
    if not ids: return
    i = 0
    mlen = str(len(ids))

    for m in ids:
        time.sleep(random.randint(1,10))
        headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Referer': 'http://www.mafengwo.cn/poi/'+m[0]+'.html'
        }
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi'
        params = { 'poi_id': m[0] }
        params = {'params': json.dumps(params)}
        #params = json.loads( jm( json.dumps(params) ) )
        response = requests.get(url,params,headers=headers)

        try:
            d = response.json()["data"]["controller_data"]["poi"]
            d = json.dumps(d,ensure_ascii = False)
            db.t_poi_u_d(m[0],d)
        except Exception as e:
            print ("poisloc Except:"+ str(e))
            print (response.text())
        i = i + 1
        print ("threads-{0}: no {1}/{2}. process {3} , finished . ".format(tid, str(i), mlen, m[0]))





    return




#step 1 获取省份、城市 ID 列表
'''
provices = ['10065' ,'10099' ,'10208' ,'10320' ,'12711' ,'12703' ,'14575' ,'12938' ,'12871' ,'14387' ,'14674' ,'12810' ,'12700' ,'14103' ,'31808' ,'12976' ,'13033' ,'13732' ,'14731' ,'12719' ,'15508' ,'14407' ,'12967' ,'12720' ,'16215' ,'12684' ,'10189' ,'10206']

for mddid in provices:
    l = city_ids(mddid,city_craw(mddid))


#step 2 获取城市内的景区

for l in open(fcity,'r',encoding='utf-8'):
    j = json.loads(l)
    if j['level'] == '2':
        aois(j['id'],aoi_craw(j['id']))


# step 3 获取景区内部景点
idls = []
for l in open(faois,'r',encoding='utf-8'):
    j = json.loads(l)
    idls.append(j['id'])
threadrun(getspot,db.t_ids_s(3),99)
'''
#db.t_c()
#db.t_mdd_a (province())
#citys(db.t_mdd_s(1))
#threadrun(aois,db.t_mdd_s(2),2)
#threadrun(pois,db.t_poi_s(4),50)
threadrun(poisloc,db.t_poi_s(),20)


for i in range(1):
    print(i)
    time.sleep(1)
    winsound.Beep(600,1000)




