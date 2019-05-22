# -*- encoding: utf-8 -*-

import threading
import requests,urllib
import json,time,re,random,datetime
import sqlite3
import js2py
from pyquery import PyQuery as pq
import mod.meetdb as db
import mod.amap as amap
import mod.logger as logger
import html
import winsound


jm = js2py.eval_js(open("mod/meet.js",'r').read())

log_name=time.strftime("meet-%Y-%m-%d.log", time.localtime())
log = logger.logger("info",log_name=log_name)

db.t_c()


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

    headers = headers if headers else {'User-Agent':agents[-1],'referer': url}
    log.info (url)

    try:
        #requests.session().keep_alive=False
        #requests.adapters.DEFAULT_RETRIES = 1
        requests.adapters.DEFAULT_RETRIES =1   # 增加重连次数
        s = requests.session()
        s.keep_alive = False   # 关闭多余连接
        s.headers= headers
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



def start():
    response = craw('https://www.meet99.com/maps/loadchild/lvyou/')
    if not response : return
    res = []
    for each in response.json():

        o = {}
        p = r'.*lvyou-(.*).html\">(.*)（(\d*).*'
        m = re.match(p,each['text'])
        o['id'],o['name'],o['count'] = m.groups()
        o['parent'] = ''
        o['sub'] = 1 if 'hasChildren' in each and each['hasChildren'] else  0
        log.debug (o)
        res.append(o)
    db.t_mdd_a(res)
    return

def mdd(ids,tid=0):

    for id in ids:
        time.sleep(random.randint(1,5))
        id = id[0]
        response = craw('https://www.meet99.com/maps/loadchild/lvyou/'+id)
        if not response : return
        res = []
        for each in response.json():
            if not each : continue
            log.debug (each)
            o = {}
            p = r'.*lvyou-(.*).html\">(.*)（(\d*).*'
            m = re.match(p,each['text'])
            o['id'],o['name'],o['count'] = m.groups()
            o['parent'] = id
            o['sub'] = 1 if 'hasChildren' in each and each['hasChildren'] else  0
            log.debug (o)
            res.append(o)
        db.t_mdd_a(res)
        db.t_mdd_u(id)

#print ("threads-{0}: no {1}/{2}. start process {3} . ".format(tid, str(i), mlen,json.dumps(params)))
#print ("threads-{0}: no {1}. process {2} , finished, fond {3} records ".format(tid,str(i),m[0], str(len(cs))))

#init()


def aoi(ids,tid=0):

    for id in ids:
        time.sleep(random.randint(1,3))
        id = id[0]
        response = craw(' https://www.meet99.com/lvyou-{}.html'.format(id))
        if not response : return

        pdoc = pq(response.content)

        res = []

        for each in pdoc('[t=""]').items():
            log.debug (each)
            url =  each('a[href^="\/jingdian-"]').attr.href
            if not url: continue
            pid = url.split('.')[0].split('-')[-1]
            name = each('a[href^="\/jingdian-"]').text()

            o = {}
            o['id'] = pid
            o['mdd'] = id
            o['name'] = name
            o['star'] = each('.cornernum').text()
            o['gone'] = each('.ever span').text()
            o['want'] = each('.never span').text()
            o['url'] = 'https://www.meet99.com'+ url

            log.debug(o)
            res.append(o)
        log.debug(res)

        if db.t_poi_append(res):
            db.t_mdd_update({'id':id,'subflag':1})

#threadrun(aoi,db.t_s('pois'),12) #获取景点图片

def down(ids,tid=0):
    i = 0

    for id in ids:


        id = id[0]
        response = craw('https://www.meet99.com/jingdian-{}.html'.format(id))
        if not response : continue
        open("cache\\meet\\{}.txt".format(id),'w',encoding='utf-8').write(response.text)

        db.t_poi_update([{'id':id,'flag':1}])
        i = i + 1
        print (i)

        if i % 50 == 0  :
             a=input('按回车')
             time.sleep(0.1)





#down(db.t_s('down'),1)
#threadrun(down,db.t_s('poi'),2)

def poi(ids,tid=0):

    for id in ids:
        log.info(id)

        id = id[0]
        try:
            content = open("cache\\meet\\{}.txt".format(id),'r',encoding='utf-8').read()
        except:
            log.error("cache\\meet\\{}.txt read is error!".format(id))
            continue

        #response = craw('https://www.meet99.com/jingdian-{}.html'.format(id))
        #if not response : continue
        pdoc = pq(content)

        img = pdoc('#curphoto > div').attr.l
        if img:
            img = 'https://i.meet99.cn'+jm(img)

        navimage = None
        if pdoc('.bd  div.img[l]'):
            navimage = 'https://i.meet99.cn'+jm(pdoc('.bd  div.img[l]').attr.l)

        detail = []
        for each in pdoc('.bd > div').items():
            s = each.html().replace('<h2>','$$$')
            s2 = re.sub(r'<.*?>','',s)
            s2 = re.sub(r'从您位置到.*?卫星地图','',s2)
            s3 = s2.split('$$$')
            s4 = [l for l in s3 if l != '' and u'驴友' not in l and u'天气预报' not in l ]
            detail += s4

        j = {}
        for item in detail:
            if u'\u3000\u3000' in item:
                key,value = item.split(u'\u3000\u3000',1)[0:2]
                j[key.replace('：','').strip()] = html.unescape(value).strip().replace(u'\u3000','')




        sub = []
        for each in pdoc('.roundbox1 > .zl').items():
            sub.append(each.html().replace('\xa0',''))

        o = {}
        o['id'] = id
        o['area'] = j[u'景区位置'] if u'景区位置' in j else ""
        o['star'] = j[u'景区资质'] if u'景区资质' in j else ""
        o['type'] = j[u'景区特色'] if u'景区特色' in j else ""
        o['line'] = j[u'游览路线'] if u'游览路线' in j else ""




        o['img'] = img if img else ""
        o['nav'] = navimage if navimage else ""


        o['text'] = json.dumps(j,ensure_ascii=False)
        o['sub'] = json.dumps(sub,ensure_ascii=False)
        o['flag'] = 2
        #log.info(o)

        db.t_poi_update([o])

poi(db.t_s('poi'),1)











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
        log.info ("threads-{0}: no {1}. process {2} , finished, fond {3} records ".format(tid,str(i),m[0], str(len(cs))))



def _poi(poiid,response):

    if not response : return

    if 'html' not in response.json()['data'] : return
    if  not  response.json()['data']['html'] : return

    ids = []

    ldoc = pq(response.json()['data']['html'])
    control = response.json()['data']['controller_data']
    log.debug (control)

    for d in ldoc('a[href^="/poi"]').items():
        go = d.find('em').text()
        o = {}
        o['id'] = d.attr.href.split('/')[-1].split('.')[0]
        o['parent'] = control['poi_id']
        o['mdd'] = ''
        o['level'] = 4
        o['name'] = d.attr.title
        log.debug (o)
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
        log.info ("threads-{0}: no {1}/{2}. process {3} , finished, fond {4} records ".format(tid, str(i), mlen, m[0], leng))



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
            log.waring ("poisloc Except:"+ str(e))
            log.waring (response.text())
        i = i + 1
        log.info ("threads-{0}: no {1}/{2}. process {3} , finished . ".format(tid, str(i), mlen, m[0]))

    return


def mfw2amap(ids,tid=1):
    g = amap.amap('958e135e16b074d7eb29e261b85a075f')
    i = 1
    for row in ids:
        time.sleep(random.randint(1,8))
        j = json.loads(row[0])
        geos =[]
        if 'lng' not in j :
            log.debug (j)
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
            log.info (j)
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
        log.debug (response.url)

        plist = pq(response.text)
        for p in plist('.a-like').items():
            id = p.attr("data-id")
            log.debug (id)
            return id
    except Exception as e:
        log.waring ("_iid Except:"+ str(e))
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
                log.debug (response.text)
                log.debug (response.url)
                if str(e) != 'Document is empty' : log.warning (e)
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
        log.info ("threads-{0}: no {1}/{2}. process {3} , finished . ".format(tid, str(i), mlen, m[0]))


    return

'''
db.t_c()    #创建表结构

db.t_mdd_a(init())  #获取省份列表

#threadrun(mdd,db.t_mdd_s(),12)   #获取景区列表

mdd(db.t_mdd_s())    #获取城市区域列表

threadrun(aois,db.t_mdd_s(2),2)   #获取景区列表

threadrun(pois,db.t_poi_s(4),50)  #获取景点列表

threadrun(poisloc,db.t_poi_s(),20) #获取景点坐标信息

threadrun(mfw2amap,db.t_poi_s_t(),120) #获取景点坐标信息


threadrun(pics,db.t_img_s(),120) #获取景点图片

province()

for i in range(1):
    time.sleep(1)
    winsound.Beep(600,1000)

'''


