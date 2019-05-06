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



jm = js2py.eval_js(open("mfw.js",'r').read())

wf = open('out\\mddid.txt','a',encoding='utf-8')
fcity = 'out\\mfw.citys.json'
faois = 'out\\mfw.aois.json'


def mdd_craw(mddid,page=1):
    url = 'https://www.mafengwo.cn/mdd/base/list/pagedata_citylist'
    params = {'mddid': mddid, 'page': page}
    params = json.loads( jm( json.dumps(params) ) )
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

    try:
        response = requests.post(url, data=params,headers=headers)
        print (params)
        if response.status_code == 200: return response.json() #list,page
    except Exception as e:
        print (e)
    return 0

def mdd_ids(mddid,content):
    ids = []

    list_doc = pq(content["list"])
    for d in list_doc('a').items():
        if 'travel-scenic-spot' in d.attr.href:
            o = {}
            o['id'] = d.attr.href.split("/")[-1].split(".")[0]
            o['parent'] = mddid
            o['level'] = '2'
            o['name'] = d.text().split("\n")[0]

            ids.append(json.dumps(o,ensure_ascii=False))
    print (ids)
    open(fcity,'a',encoding='utf-8').write('\n'.join(ids)+"\n")


    page_doc = pq(content["page"])  #print (page_doc.html())
    if  page_doc(".pg-next"):
        ipage = page_doc(".pg-next").attr("data-page")
        rs = mdd_craw(mddid,ipage)
        mdd_ids(mddid,rs)


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



#step 1 获取省份、城市 ID 列表
'''
provices = ['10065' ,'10099' ,'10208' ,'10320' ,'12711' ,'12703' ,'14575' ,'12938' ,'12871' ,'14387' ,'14674' ,'12810' ,'12700' ,'14103' ,'31808' ,'12976' ,'13033' ,'13732' ,'14731' ,'12719' ,'15508' ,'14407' ,'12967' ,'12720' ,'16215' ,'12684' ,'10189' ,'10206']

for mddid in provices:
    l = city_ids(mddid,city_craw(mddid))
'''

#step 2 获取城市内的景区

for l in open(fcity,'r',encoding='utf-8'):
    j = json.loads(l)
    if j['level'] == '2':
        aois(j['id'],aoi_craw(j['id']))











