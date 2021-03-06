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
import requests,urllib
import json,time,re,random,datetime
import sqlite3
import js2py
from pyquery import PyQuery as pq
import mod.db as db
import mod.amap as amap
import winsound


jm = js2py.eval_js(open("mod/mfw.js",'r').read())
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
            db.t_poi_u_t(m[0],d)
        except Exception as e:
            print ("poisloc Except:"+ str(e))
            print (response.text())
        i = i + 1
        print ("threads-{0}: no {1}/{2}. process {3} , finished . ".format(tid, str(i), mlen, m[0]))

    return


def mfw2amap(ids,tid=1):
    g = amap.amap('958e135e16b074d7eb29e261b85a075f')
    i = 1
    for row in ids:
        time.sleep(random.randint(1,8))
        j = json.loads(row[0])
        geos =[]
        if 'lng' not in j :
            print (j)
            continue

        geo = g.regeo(str(j['lng']),str(j['lat']))

        found = None

        aois = geo['regeocode']['aois']

        for p in aois:
            p['level'] = 'aoi'
            x,y = p['location'].split(',')
            if p['distance'] == '0' and str(j['lng']) == x and str(j['lat']) == y :
                if p['name'] in j['name'] or j['name'] in p['name']:
                    found = {'id':p['id'],'name':p['name'],'location':p['location']}
                    break

        pois = geo['regeocode']['pois']

        for p in pois:
            p['level'] = 'poi'
            if p['distance'] == '0' :
                found = {'id':p['id'],'name':p['name'],'location':p['location'],'address':p['address']}
                if p['name'] in j['name'] or j['name'] in p['name']:
                    found = {'id':p['id'],'name':p['name'],'location':p['location']}
                    break
            else :
                p['distance'] = float(p['distance'])
                geos.append(p)




        # aois  pois 都有找到 distance=0 时， 优先 pois!

        if not found and geos:
            geos.sort(key=lambda item: item.get('distance'),reverse=False)
            for p in geos:
                if float(geos[0]['distance']) < 5:
                    if p['name'] in j['name'] or j['name'] in p['name']:
                        found = {'id':p['id'],'name':p['name'],'location':p['location'],'address':p['address']}


        if found:
            aid = found['id']
            atext = json.dumps(found,ensure_ascii = False)
            mid = j['id']
            print (j)
            db.t_poi_u_a(aid,atext,mid)
        else:
            #print (geos)
            mid = j['id']
            db.t_poi_u_a('1','',mid)



def _iid(mid):
    headers ={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    'Referer': 'http://www.mafengwo.cn/photo/poi/'+mid+'.html'
    }
    url = 'http://www.mafengwo.cn/mdd/ajax_photolist.php'
    params = {
    'act': 'getPoiPhotoList',
    'poiid': mid,
    'page' : 1
    }


    try:
        response = requests.get(url,params,headers=headers)
        print (response.url)

        plist = pq(response.text)
        for p in plist('.a-like').items():
            id = p.attr("data-id")
            print (id)
            return id
    except Exception as e:
        print ("_iid Except:"+ str(e))
        return

def pics(ids,tid=1):
    if not ids: return
    i = 0
    mlen = str(len(ids))

    for m in ids:
        i = i + 1
        time.sleep(random.randint(1,10))
        iid = _iid(m[0])
        aid = m[1]
        if not iid:
            db.t_img_a_p(m[0])
            continue


        headers ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Referer': 'http://www.mafengwo.cn/photo/poi/'+m[0]+"_"+iid+'.html'
        }
        url = 'http://www.mafengwo.cn/mdd/ajax_photolist.php'

        page = 0
        ps = []
        while (True):
            page += 1
            if page > 3 : break
            params = {
            'act': 'getThumbList',
            'placeId': m[0],
            'type': 1,
            'initId': iid,
            'page': page
            }

            #print ("threads-{0}: no {1}/{2}. start process {3} . ".format(tid, str(i), mlen,json.dumps(params)))
            try:
                response = requests.post(url,data=params,headers=headers)
                ldoc = pq(response.json()['html'])

            except Exception as e:
                #print (response.text)
                #print (response.url)
                if str(e) != 'Document is empty' : print (e)
                break

            for item in ldoc('li').items():
                iid = item.attr('data-id')
                o = {}
                o['pid'] = item.attr('data-id')
                o['poi'] = item.attr('data-placeid')
                o['aid'] = aid

                o['name'] = item.attr('data-placename')
                hw = urllib.parse.unquote(item.attr('data-imgbig'))

                w,h = map(int, hw.split("!")[1].split('r')[0].split('x'))
                o['direct'] = 0 if (w> h) else 1
                sdate = item.attr('data-time').split(" ")[0]
                o['y'],o['m'],o['d'] = map(int, sdate.split("-"))
                o['url'] = hw.split('!')[0]
                if o['direct'] == 0 :
                    o['url'] += '640'
                else:
                    o['url'] += 'x640'
                ps.append(o)


        db.t_img_a(ps)
        print ("threads-{0}: no {1}/{2}. process {3} , finished . ".format(tid, str(i), mlen, m[0]))


    return


db.t_c()    #创建表结构
'''
db.t_mdd_a(province())  #获取省份列表

citys(db.t_mdd_s(1))    #获取城市区域列表

threadrun(aois,db.t_mdd_s(2),2)   #获取景区列表

threadrun(pois,db.t_poi_s(4),50)  #获取景点列表

threadrun(poisloc,db.t_poi_s(),20) #获取景点坐标信息

threadrun(mfw2amap,db.t_poi_s_t(),120) #获取景点坐标信息

'''
threadrun(pics,db.t_img_s(),120) #获取景点图片


for i in range(1):
    time.sleep(1)
    winsound.Beep(600,1000)




