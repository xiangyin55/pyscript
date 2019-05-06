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


class gaode:
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
    def _get_poi_page(self,city,keywords,page):

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
    def get_poi_all(self,city, keywords, type='all',count=-1 ):

        pois = []
        i = 1

        while True:  # 使用while循环不断分页获取数据
            result = self._get_poi_page(city, keywords, i)
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




    def _get_polygon_page(self, keywords,polygon,page):
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
    def get_polygon_all(self,keywords,polygon):
        i = 1
        pois = []

        while True:  # 使用while循环不断分页获取数据
            result = self._get_polygon_page(keywords,polygon, i)


            if  not result or not 'count' in result or result['count'] == '0':
                break
            for poi in result['pois']:
                if u'风景名胜' in poi['type']:
                    pois.append(poi)
            i = i + 1
        return pois


    def get_poi_detail_byid (self,id):

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

    def get_poi_detail_byid_old (self,id):
        parameters = { 'id': id }
        try:
            response = requests.get(self.poi_detail_url, parameters)
            rest = response.json()
        except Exception as err:
            print (err)
            rest = {}
        return rest

    def get_poi_summary_byid (self,id):

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

    #根据id获取边界数据
    def get_boun_form_json (self,data):

        if data['status'] == "1":
            rest = data['data']['spec']
            if len(rest) ==1:
                return ""
            if 'mining_shape' in rest:
                return rest['mining_shape']['shape']
        else:
            return ""


    #数据写入json文件
    def wirte_2_json(self, pois ,city, keywords):
        wf= open( self.outdir + city + "_" + keywords + '.json','w',encoding='utf-8')
        for l in pois:
            if u'风景名胜' in l['type']:
                wf.write(json.dumps(l,ensure_ascii = False)+"\n")
        wf.close()

    def get_district(self,keywords,level):
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


    def get_aoi_byid(self,poiid='B022F0071G'):

        #获取景区详细信息，已获得景点的范围数据
        js = self.get_poi_detail_byid(poiid)

        # 如果景区数据获取失败，直接返回NULL
        if not js or js['status'] != "1" :
            print (js)
            return

        #获取景区范围数据
        path = self.get_boun_form_json(js)

        #print (path)
        # 如果景区没有范围数据，直接返回景区数据
        if not path :
            return js


        # 获取景区内所有景点
        rests = self.get_polygon_all("景点",path.replace(";","|"))
        print (len(rests))

        #保存摘要信息
        wf_s = open("aoi_"+poiid+"_summary.txt",'w',encoding='utf-8')
        li_s = []
        for i in range(0,len(rests)):
            li_s.append(rests[i]['id'])
            wf_s.write(json.dumps(rests[i],ensure_ascii = False)+"\n")

        wf_s.close()

        #保存详细信息
        self.sav_aoi_2_raw_file(li_s,poiid)


    def sav_aoi_2_raw_file(self,poi_list,aoi_id,start=0,end=-1,mode='w'):
        #保存详细信息

        if start > len(poi_list):
            print('start > poi length, return !')
            return
        elif end <= start:
            end = len(poi_list)

        wf_d = open("aoi_"+aoi_id+"_details.txt",mode,encoding='utf-8')

        for i in range(start,end):
            print ('正在处理: {0}/{1}'.format(i+1-start,end-start))
            ss = g.get_poi_detail_byid(poi_list[i].strip())
            if ('status' in ss and ss['status'] == '8'):
                print (ss)
                continue
            elif ('status' in ss and ss['status'] != '1'):
                print (ss)
                break
            wf_d.write(json.dumps(ss,ensure_ascii = False)+"\n")
        wf_d.close()

        return

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


    # 将get_poi_detail_byid获得的json内容，按景区进行分类，提取重要信息

    def sav_raw_2_js_file(self,raw_file_name):
        ids = []
        dupli = []
        rests = []
        evals = []
        fg = ["4A景区","景区","5A景区","山峰","文物古迹","3A景区","寺庙","广场","公园","主题公园","2A景区","森林公园","温泉","道观","纪念馆","教堂","动物园","水族馆","植物园","博物馆","港口码头","游乐园","展览馆","桥","海滨浴场","湿地公园","水系","文化宫","美术馆","度假村"]
        raw = open(raw_file_name,'r',encoding='utf-8')
        a5 = open(u'raw\\a5.txt','w',encoding='utf-8')
        a4 = open(u'raw\\a4.txt','w',encoding='utf-8')
        ot = open(u'raw\\sub.txt','w',encoding='utf-8')
        evfile = open(u'raw\\eval.txt','w',encoding='utf-8')

        cf_count = 0

        i = 0

        for l in raw :
            i = i + 1
            if (i % 1000 == 0):
                print ('已处理{0}行!'.format(i))

            if (l) :
                r = {}  #规整后的json对象
                j = json.loads(l)



                # 获取基础信息
                r['_id'] = j['data']['base']['poiid']

                summary = self.get_poi_summary_byid( r['_id'] )
                if summary['status'] == "1":
                    r['pcode'] = summary['pois'][0]['pcode']
                break;



                if 'geodata' in  j['data']['base'] and 'aoi' in  j['data']['base']['geodata'] and  len(j['data']['base']['geodata']['aoi']) > 0:
                    r['parent'] = j['data']['base']['geodata']['aoi'][0]['mainpoi']
                else:
                    r['parent'] = ""
                if r['parent'] == r['_id']:
                    r['parent'] = ""
                r['name'] = j['data']['base']['name']


                #过滤重复的ID
                if r['_id'] in ids:
                    cf_count += 1
                    dupli.append({'id': r['_id'],'name': r['name']})
                    continue
                ids.append(r['_id'])

                r['alias'] = j['data']['base']['alias_name'] if 'alias_name' in j['data']['base'] else ""
                r['x'] = j['data']['base']['x']
                r['y'] = j['data']['base']['y']
                r['city'] =  j['data']['base']['city_name']
                r['adcode'] =  j['data']['base']['city_adcode']
                r['address'] =  j['data']['base']['address']
                r['metry'] = j['data']['base']['navi_geometry'] if 'navi_geometry' in  j['data']['base'] else ""
                r['tag'] = j['data']['base']['std_t_tag_0_v'] if 'std_t_tag_0_v' in j['data']['base'] else "景点"
                r['score'] = float(j['data']['score']['总分']) if ('score' in j['data'] and '总分' in j['data']['score']) else 3.33
                r['shape'] = j['data']['spec']['mining_shape']['shape'] if ('mining_shape' in j['data']['spec']) else ""
                r['shape_rectangle'] = self.calc_rectangle(r['shape']) if  r['shape'] else ""
                r['zoom'] =  j['data']['spec']['mining_shape']['level'] if ('mining_shape' in j['data']['spec']) else '16'
                r['season_dest'] = j['data']['scenic']['season_desc']  if ('scenic' in j['data'] and 'season_desc' in j['data']['scenic']) else ""
                r['season'] = j['data']['scenic']['season'] if ('scenic' in j['data'] and 'season' in j['data']['scenic']) else []
                r['cover'] = j['data']['pic_cover']['url']  if ('pic_cover' in j['data'] and 'url' in j['data']['pic_cover'] ) else ""
                r['intro'] = j['data']['scenic']['intro'] if ('scenic' in j['data'] and 'intro' in j['data']['scenic']) else ""

                #rests.append(r)


                if r['intro']:
                    ev = {}
                    ev['poiid'] = r['_id']
                    ev['parent'] = r['parent']
                    ev['name'] = r['alias'] if r['alias'] else r['name'].split("-")[-1].strip()
                    ev['tag'] = r['tag']
                    ev['text'] = r['intro']
                    ev['pic'] = []
                    if 'pic' in j['data']:
                        for p in j['data']['pic']:
                            ev['pic'].append(p['url'])
                    if ev['text'] and ev['pic']:
                        evals.append(ev)

                if 'comment' in j['data']['review']:
                    b_r = False
                    for c in j['data']['review']['comment']:
                        ev = {}
                        ev['poiid'] = r['_id']
                        ev['parent'] = r['parent']
                        ev['name'] = r['alias'] if r['alias'] else r['name'].split("-")[-1].strip()
                        ev['tag'] = r['tag']
                        ev['text'] = c['review']
                        ev['pic'] =[]
                        if 'pic_info' in c :
                            for p in c['pic_info']:
                                ev['pic'].append(p['url'])
                        if ev['text'] and ev['pic']:
                            b_r = True
                            evals.append(ev)
                    if (b_r) : rests.append(r)


        print(cf_count)
        rests.sort(key=lambda x: x["score"],reverse=True)
        evals.sort(key=lambda x: x['poiid'],reverse=True)


        # 分类保存

        for j in rests:

            if j['tag'] == "5A景区":
                a5.write(json.dumps(j,ensure_ascii = False)+"\n")
            elif j['tag'] == "4A景区" or j['parent'] == "":
                a4.write(json.dumps(j,ensure_ascii = False)+"\n")
            else:
                ot.write(json.dumps(j,ensure_ascii = False)+"\n")

        for e in evals:
            evfile.write(json.dumps(e,ensure_ascii = False)+"\n")


        a5.close()
        a4.close()
        ot.close()
        evfile.close()



def getdetail(tasklist,no):
    ids = []
    open("raw\\"+adcodes[num]+"0000_scenic_ids.json",'a',encoding='utf-8')
    ids = open("raw\\"+adcodes[num]+"0000_scenic_ids.json",'r',encoding='utf-8').read().split('\n')

    wf = open("raw\\"+adcodes[num]+"0000_scenic_raw.json",'a',encoding='utf-8')
    wf_ids = open("raw\\"+adcodes[num]+"0000_scenic_ids.json",'a',encoding='utf-8')
    i = 0
    j = 0
    for id in tasklist:
        i = i + 1
        id = id.strip()
        if (id not in ids):
            time.sleep(random.uniform(0, 5) )
            j = j + 1
            print ("Thread:"+str(no) +" " +str(i)+"("+ str(j) +") :" + id)
            ss = g.get_poi_detail_byid(id)
            if (not ss):  break
            wf.write(json.dumps(ss,ensure_ascii = False)+"\n")
            wf_ids.write(id+"\n")
            ids.append(id)
            time.sleep(5)

    wf.close()
    wf_ids.close()


if __name__ == '__main__':

    print("This is api for gaode!")
    adcodes = ["34","11","44","41","15","23","65","42","21","37","32","61","31","52","50","54","35","43","46","63","45","64","36","33","13","71","81","82","62","51","22","12","53","14"]
    step_one , step_two , step_thr = True , True , True
    step_one , step_two ,step_thr = False , False ,True

    i = 0
    for code in range(34):
        j = 0
        for l in open("raw\\"+adcodes[code]+"0000_pois_ids.json",'r',encoding='utf-8'):
            i = i + 1
            j = j + 1
        print (adcodes[code]+":"+str(j))
    print (i)



    num = 1
    threadNum = 100
    g = gaode('958e135e16b074d7eb29e261b85a075f')
#    g = gaode()

    '''
    step 1: 获取所有城市区号, 输出到 out\cityadcode.json 文件
    '''
    if (step_one):
        wf = open("raw\\"+adcodes[num]+"0000.json",'w',encoding='utf-8')
        cityadcode = []
        ss =  g.get_district('100000',3)
        # 仅仅添加第三级，其他级别不添加
        for p in ss['districts'][0]['districts']:
            for l in p['districts']:
                for m in l['districts']:
                    if m['adcode'][0:2] == adcodes[num] and m['adcode'] not in cityadcode :   #取省份
                        cityadcode.append(m['adcode'])
                if l['adcode'][0:2] == adcodes[num] and l['adcode'] not in cityadcode: #取省份
                    cityadcode.append(l['adcode'])


        wf.write('\n'.join(cityadcode))
        wf.close()
        print("Step One is Over!")

    '''
    step 2: 获取城市所有POI,
    输出到:
         out\pois_raw.json  原始内容
         out\pois_ids.json  ID列表
    '''

    if (step_two):
        ids = []
        wf = open("raw\\"+adcodes[num]+"0000_pois_raw.json",'w',encoding='utf-8')
        wf_ids = open("raw\\"+adcodes[num]+"0000_pois_ids.json",'w',encoding='utf-8')
        for city in open("raw\\"+adcodes[num]+"0000.json",'r',encoding='utf-8'):
            city = city.strip()
            print (city)
            for ss in g.get_poi_all(city,'景点'):
                #print (ss)
                if (ss['id'] not in ids):
                    wf.write(json.dumps(ss,ensure_ascii = False)+"\n")
                    wf_ids.write(ss['id']+"\n")
                    ids.append(ss['id'])
        wf.close()
        wf_ids.close()
        print("Step Two is Over!")

    '''
    step 3: 获取POI详细信息,
    输出到:
         out\scenic_raw.json  原始内容
    '''
    if (step_thr):

        #创建线程
        threads = []
        task = {}
        i = 0
        for id in open("raw\\"+adcodes[num]+"0000_pois_ids.json",'r',encoding='utf-8'):
            i = i + 1
            mod = i % threadNum
            if (mod not in task): task[mod] = []
            task[mod].append(id)

        for i in range(threadNum):
            t = threading.Thread(target=getdetail,args=(task[i],i))
            threads.append(t)

        for i in range(threadNum):
            threads[i].start()

        for i in range(threadNum):
            threads[i].join()

        print ('step 3 is over!!')