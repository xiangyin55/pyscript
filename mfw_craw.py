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
import mod.db as db
from pyquery import PyQuery as pq


if 'ldebug' not in locals().keys() : ldebug = True
jm = js2py.eval_js(open("mfw.js",'r').read())


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

def craw(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    #print (url)

    try:
        response = requests.get(url,headers=headers)
        if response.status_code == requests.codes.ok :
            return response
        elif response.status_code == 403:
            print ('Request Error 403')
            exit('403')
        else:
            print (response.status_code)

    except Exception as e:
        print (response.url)
        print (e)
    return 0


def province(response):
    if not response : return
    ids = []
    listdoc = pq(response.text)('.hot_city > .clearfix')

    for each in listdoc('a[href^="http://z.mafengwo.cn/jd/"]').items():
        if each.attr.href == response.url : continue
        o = {}
        o['id'] = each.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = ''
        o['level'] = 1
        o['name'] = each.text().split(u"（")[0].replace('"','').replace("'",'')
        ids.append(o)
        print (json.dumps(o,ensure_ascii = False))
    return ids

def city(response):
    if not response : return
    ids = []
    listdoc = pq(response.text)('.hot_travel')
    i = 0
    for each in listdoc('a[href^="http://z.mafengwo.cn/jd/"]').items():
        i = i +1
        if each.attr.href == "http://z.mafengwo.cn/jd/" : continue
        if each.attr.href == response.url : continue
        if u"旅游景点" in each.text() :
            print (each.text())
            continue
        o = {}
        o['id'] = each.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = response.url.split('/')[-1].split('.')[0]
        o['level'] = 2
        o['name'] = each.text().split("\n")[0].split(u"（")[0].replace('"','').replace("'",'')
        ids.append(o)
        #print (json.dumps(o,ensure_ascii = False))

    return ids

def area(response):
    if not response : return
    listdoc = pq(response.text)('.white_bg.m_t_30 > .col')
    ids = []
    for each in listdoc('a[href^="http://www.mafengwo.cn/poi/"]').items():
        if each.attr.href == "http://z.mafengwo.cn/jd/" : continue
        if each.attr.href == response.url : continue

        o = {}
        o['id'] = each.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = ''
        o['area'] = response.url.split('/')[-1].split('.')[0]
        o['level'] = 3
        o['name'] = each.text().split("\n")[0].replace('"','').replace("'",'')
        ids.append(o)
        #print (json.dumps(o,ensure_ascii = False))
    return ids

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
        o['area'] = ''
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




def getcity(ids,t_no=1):
    if not ids: return
    for r in ids:
        url = 'http://z.mafengwo.cn/jd/'+r[0]+'.html'
        if ldebug :print (url)
        cs = city(craw(url))
        if ldebug :print (cs)
        db.t_area_a(cs)
        #print ("threads-{0}: process {1} finished!".format(t_no,r[0]))


def getarea(ids,t_no=1):
    if not ids : return
    for r in ids:
        url = 'http://z.mafengwo.cn/jd/'+r[0]+'.html'
        if ldebug :print (url)
        ars = area(craw(url))
        if (ars == []): db.t_ids_u(r[0],2)
        else: db.t_ids_a(ars)
        time.sleep(5)
        print ("threads-{0}: process {1} finished!".format(t_no,r[0]))

def getspot(ids,t_no=1):
    if not ids: return
    i = 0
    for r in ids:
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiSubPoiApi?params={"poi_id":"'+r[0]+'","type":"3"}'
        if ldebug :print (url)

        ss = spot(craw(url))
        if ldebug :print (ss)
        if (ss == []): db.t_ids_u(r[0],3)
        db.t_ids_a(ss)
        time.sleep(5)
        i = i+1
        print ("threads-{0}: no {1}. process {2} finished! ".format(t_no,str(i),r[0]))
    return

def getinfo(ids,t_no=1):
    if not ids: return


    for r in ids:
        headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Referer': 'http://www.mafengwo.cn/poi/'+r[0]+'.html'
        }
        url = 'http://pagelet.mafengwo.cn/poi/pagelet/poiLocationApi'
        params = { 'poi_id': r[0] }
        params = {'params': json.dumps(params)}
        #params = json.loads( jm( json.dumps(params) ) )
        response = requests.get(url,params,headers=headers)

        print (response.json())
        break

    return





db.t_c()

#db.t_area_a(province(craw('http://z.mafengwo.cn/jd')))


#threadrun(getcity,db.t_area_s(1),5)
#threadrun(getarea,db.t_area_s(2),50)

#threadrun(getspot,db.t_ids_s(3),9)

'''



'''
getinfo([['778']])






