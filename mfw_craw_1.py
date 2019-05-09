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


jm = js2py.eval_js(open("mfw.js",'r').read())
ld = True

fcity = 'out\\mfw.citys.json'
faois = 'out\\mfw.aois.json'
fpois = 'out\\mfw.pois.json'



def threadrun(func,ids,tcount):
    threads = []
    task = {}
    i = 0
    for id in ids:
        i = i + 1
        mod = i % tcount
        if (mod not in task): task[mod] = []
        task[mod].append(id)

    for i in range(tcount):
        t = threading.Thread(target=func,args=(task[i],i))
        threads.append(t)

    for i in range(tcount):
        threads[i].start()

    for i in range(tcount):
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

def mdd_s():

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
        if ld : print (json.dumps(o,ensure_ascii = False))

    return ss

def mdd(response,mddid):
    ds = []
    if response == None : return

    ldoc = pq(response.json()["list"])
    for d in ldoc('a').items():
        if 'travel-scenic-spot' in d.attr.href:
            o = {}
            o['id'] = d.attr.href.split("/")[-1].split(".")[0]
            o['parent'] = mddid
            o['level'] = 2
            o['name'] = d.text().split("\n")[0]

            ds.append(o)


    pdoc = pq(response.json()["page"])  #print (page_doc.html())
    if  pdoc(".pg-next"):
        url = 'https://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        ipage = pdoc(".pg-next").attr("data-page")
        params = {'mddid': mddid, 'page': ipage }
        params = json.loads( jm( json.dumps(params)))
        rs = craw(url,params,method='post')
        ds = ds + mdd(rs,mddid)

    return ds

def mdd_c(mdds):
    if not mdds : return

    for m in mdds:
        cs = []
        url = 'https://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
        params = {'mddid': m[0], 'page': 1}
        params = json.loads( jm( json.dumps(params)))

        response = craw(url,params,method='post')
        cs = mdd(response,m[0])

        db.t_mdd_a(cs)

        print (len(cs))



def aoi_craw(aoiid,page=1):

    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    url ='https://www.mafengwo.cn/ajax/router.php'

    params = {
    'iMddid' : aoiid,
    'iPage': page,
    'iTagId': '0',
    'sAct': 'KMdd_StructWebAjax|GetPoisByTag'
    }
    params = json.loads( jm( json.dumps(params) ) )

    try:
        response = requests.get(url, params,headers=headers)
        print (response.url)
        if response.status_code == 200: return response.json()['data']
    except Exception as e:
        print (e)
    return 0



def aois(aoiid,content):
    ids = []

    if not content : return

    if content["page"] :
        list_doc = pq(content["list"])
        for d in list_doc('a').items():
            o = {}
            o['id'] = d.attr.href.split("/")[-1].split(".")[0]
            o['parent'] = aoiid
            o['level'] = '3'
            o['name'] = d.text().split("\n")[0]
            ids.append(json.dumps(o,ensure_ascii=False))
        print (ids)
        open(faois,'a',encoding='utf-8').write('\n'.join(ids)+"\n")

    if content["page"]:
        page_doc = pq(content["page"])  #print (page_doc.html())
        if  page_doc(".pg-next"):
            ipage = page_doc(".pg-next").attr("data-page")
            rs = aoi_craw(aoiid,ipage)
            aois(aoiid,rs)


def poi_craw(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    #print (url)

    try:
        response = requests.get(url,headers=headers)
        if response.status_code == requests.codes.ok :
            return response
        else:
            print (response.status_code)

    except Exception as e:
        print (response.url)
        print (e)
    return 0


def spot(response):

    if not response : return
    if 'html' not in response.json()['data'] : return
    if  not  response.json()['data']['html'] : return

    ids = []

    listdoc = pq(response.json()['data']['html'])
    control = response.json()['data']['controller_data']
    #print (control)

    for d in listdoc('a[href^="/poi"]').items():
        go = d.find('em').text()
        o = {}
        o['id'] = d.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = control['poi_id']
        o['level'] = 4
        o['name'] = d.attr.title
        #print (o)
        ids.append(o)


    if control['hasMore'] :
        page = control['curPage'] + 1
        poi = control['poi_id']
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+str(poi)+'","type":3,"page":'+str(page)+'}'
        s = spot(craw(url))
        ids = ids + s
    return ids


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
db.t_c()
db.t_mdd_a (mdd_s())
mdd_c(db.t_mdd_s(1))







