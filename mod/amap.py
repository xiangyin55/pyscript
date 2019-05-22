# -*- encoding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        api_gaode
# Purpose:
#
# Author:      Administrator
#
# Created:     12/03/2019
# Copyright:   (c) Administrator 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import threading
import requests
import json
import time
import re
import random


class amap:
    outdir = u"./out/"

    poi_search_url = "http://restapi.amap.com/v3/place/text"
    poi_polygon_url = "http://restapi.amap.com/v3/place/polygon"
    poi_summary_url = "http://restapi.amap.com/v3/place/detail"
    poi_detail_url = "https://ditu.amap.com/detail/get/detail"
    poi_district_url = "http://restapi.amap.com/v3/config/district"


#   def  __init__ (self,key = "c69bd09bde2e2a17eff5edf9b89720a5"):

    def  __init__ (self,key = "958e135e16b074d7eb29e261b85a075f"):
        self.amap_web_key = key
        return


    # 单页获取pois
    def _poi(self,city,keywords,page):

        parameters = {
            'keywords': keywords ,
            'city': city ,
            'extensions': 'all',
            'citylimit': True,
            'output': 'json',
            'key': self.amap_web_key,
            'type' : u'风景名胜' ,
            'offset':'50' ,
            'page': page
        }


        try:
            response = requests.get(self.poi_search_url, parameters)
            rest = response.json()
        except  Exception as e:
            print(e)
            rest = {'status': '-1', 'count':'0' , 'pois':[] }
        return rest



    # 根据城市名称和分类关键字获取poi数据
    def pois(self,city, keywords, type='all',count=-1 ):

        pois = []
        i = 1

        while True:  # 使用while循环不断分页获取数据
            result = self._poi(city, keywords, i)
            if  (not result['status'] or result['count'] == '0' or len(result['pois'])==0 ):
                break
            for poi in result['pois']:
                if type=='parent' and u'风景名胜' in poi['type'] and not poi['parent'] and '-' not in poi['name'] and u'暂停营业' not in poi['name'] :
                    pois.append(poi)
                elif u'风景名胜' in poi['type']:
                    pois.append(poi)
            if count > 0 and len(pois) >= count:
                return(pois[0:count-1])

            i = i + 1
        print ( i-1)
        print (len(pois))

        return pois




    def _polygon(self, keywords,polygon,page):
        parameters = {
            'keywords': keywords ,
            'polygon': polygon,
            'city': '010' ,
            'extensions': 'all',
            'citylimit': True,
            'output': 'json',
            'key': self.amap_web_key,
            'type' : u'风景名胜' ,
            'offset':'100' ,
            'page': page
        }
        try:
            response = requests.get(self.poi_polygon_url, parameters)
            rest = response.json()

        except  Exception as e:
            print(e)
            rest = {}

        return rest

    # 获得一个区域内所有的景点信息
    def polygons(self,keywords,polygon):
        i = 1
        pois = []

        while True:  # 使用while循环不断分页获取数据
            result = self._polygon(keywords,polygon, i)


            if  not result or not 'count' in result or result['count'] == '0':
                break
            for poi in result['pois']:
                if u'风景名胜' in poi['type']:
                    pois.append(poi)
            i = i + 1
        return pois


    def detail (self,id):

        parameters = { 'id': id }

        try:
            url = "https://www.amap.com/detail/"+id.strip()
            heads = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
            response = requests.get(url,headers=heads)
            #print (response.headers)
            #print (response)

            #print (response.text)
            content = re.search(u'window.detail(.*)',response.text).group()
            content = re.sub('window.detail =','',content)
            content = re.sub('};','}',content

            )
            rest = json.loads(content);
            #rest = response.json()
        except Exception as err:
            print (err)
            print (url)
            rest = {}
        return rest

    def detail_old (self,id):
        parameters = { 'id': id }
        try:
            response = requests.get(self.poi_detail_url, parameters)
            rest = response.json()
        except Exception as err:
            print (err)
            rest = {}
        return rest

    def summary (self,id):
        parameters = {
        'key': self.amap_web_key,
        'id': id,
        }

        try:
            response = requests.get(self.poi_summary_url, parameters)
            rest = response.json()
        except :
            rest = {}
        return rest



    def district(self,keywords,level):
        parameters = {
            'key': self.amap_web_key,
            'keywords': keywords ,
            'subdistrict': level ,
            'extensions': 'base',
        }
        response = requests.get(self.poi_district_url, parameters)
        print (response.url)
        data = response.json()
        return data

    def regeo(self,lng,lat):
        url = 'https://restapi.amap.com/v3/geocode/regeo'
        parameters = {
            'key': self.amap_web_key,
            'location': "{},{}".format(lng,lat),
            'radius': 100 ,
            'extensions': 'all',
        }
        response = requests.get(url, parameters)
        #print (response.url)
        data = response.json()

        return data



    def calc_rectangle(self, path):
        lng_min,lat_min,lng_max,lat_max =['','','',''];

        for s in path.split(";"):
            a,b = s.split(',')
            lng_min = a if lng_min else ""
            if (a < lng_min or not lng_min ): lng_min = a
            if (a > lng_max or not lng_max): lng_max = a
            if b < lat_min or  not lat_min: lat_min = b
            if b > lat_max or not lat_max : lat_max = b
        #print('{0},{1};{2},{3}'.format(lng_min,lat_min,lng_max,lat_max))
        return '{0},{1},{2},{3}'.format(lng_min,lat_min,lng_max,lat_max)


