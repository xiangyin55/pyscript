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
import json
import time
import re
import random
import sqlite3

def calc_rectangle(path):
    if not path : return ""
    lng_min,lat_min,lng_max,lat_max =['','','',''];

    try:

        for s in path.split(";"):
            a,b = s.split(',')
            lng_min = a if lng_min else ""
            if (a < lng_min or not lng_min ): lng_min = a
            if (a > lng_max or not lng_max): lng_max = a
            if b < lat_min or  not lat_min: lat_min = b
            if b > lat_max or not lat_max : lat_max = b
    except Exception as e:
        print (e)
        return ""
    #print('{0},{1};{2},{3}'.format(lng_min,lat_min,lng_max,lat_max))
    return '{0},{1},{2},{3}'.format(lng_min,lat_min,lng_max,lat_max)

def pick(f_raw):
    scenids = []   #挑选前所有的景点数据
    scenics = []   #挑选前所有的景点数据
    pickids = []   #挑选后的景点ID列表
    picks = []     #挑选后的景点数据
    nupicks = []   #挑选后的放弃景点数据
    nuaoi = []     #没有采集的aoi ID列表
    fils =  ['充电站','管理处','暂停营业','建设中','装修中','交口处','导览图','缆车下站','总台','管理班','项目部','自助售卖机','保安亭','调度室']

    for l in open(f_raw,'r',encoding='utf-8'):
        try:
            j = json.loads(l)


            id = j['base']['poiid']
            name = j['base']['name']
            aoi =  j['base']['geodata']['aoi'][0]['mainpoi'] if ('geodata' in j['base'] and j['base']['geodata']['aoi'] and len(j['base']['geodata']['aoi'])>0) else ""
            level = j['scenic']['level'] if ('scenic' in j and 'level' in j['scenic']  and j['scenic']['level']) else ""
            score = j['scenic']['src_star'] if ('scenic' in j and 'src_star' in j['scenic'] and j['scenic']['src_star'])  else "0"
            intro = j['scenic']['intro'] if ('scenic' in j  and 'intro' in j['scenic'] and ( j['scenic']['intro']))  else ""
            cover = j['pic_cover']['url'] if ('pic_cover' in j  and  'url' in j['pic_cover']) else ""
            level = level.strip()

        except:
            print (l)
            continue

        scenics.append(j)
        scenids.append(id)




#        if  level in ['AAA','AAAA','AAAAA'] and (aoi == id or aoi=="") :
        if  level in ['AAA','AAAA','AAAAA']:

            if  (id and id not in pickids):
                pickids.append(id)
        '''
        if  (aoi and aoi not in scenids):
            pickids.append(aoi)
        if  (aoi == id):
            if  (id and id not in pickids):
                pickids.append(id)
        if  intro and id not in pickids:
            pickids.append(id)
        '''

    print ("null filter Pickids len is {0}".format(str(len(pickids))))
    at, pickids = pickids, []
    for id in at:
        if id in scenids:
            pickids.append(id)
        else :
            nuaoi.append(id)
            print (id)
    print ("Pickids len is {0}".format(str(len(pickids))))

    for j in scenics:

        try:
            id = j['base']['poiid']
            name = j['base']['name']
            aoi =  j['base']['geodata']['aoi'][0]['mainpoi'] if (j['base']['geodata']['aoi'] and len(j['base']['geodata']['aoi'])>0) else ""
            intro = j['scenic']['intro'] if (('scenic' in j )and ('intro' in j['scenic']) and ( j['scenic']['intro']))  else ""
            cover = j['pic_cover']['url'] if ('pic_cover' in j  and  'url' in j['pic_cover']) else ""
            '''
            if not intro : nupicks.append(j)
            elif not cover : nupicks.append(j)
            '''
            bfil = False
            for fi in fils:
                if fi in name : bfil = True

            if (not bfil)  and ( id in pickids or  aoi in pickids): picks.append(j)
            else: nupicks.append(j)
        except Exception as e:
            print (e)
            print(j['base']['id'])
            nupicks.append(j)

    return {'pickpoi':picks,'nupicks':nupicks,'nuaoi':nuaoi}


def spec(pois,ad):
    citys = {}
    f_poi = 'raw\\'+ad+'0000_pois_raw.json'
    for l in open(f_poi,'r',encoding='utf-8'):
        j = json.loads(l)
        id = j['id']
        citys[id] = j['cityname'],j['adcode'][0:4]+"00"

    specs = []

    for j in pois:
        s = {}
        try:
            s['id'] = j['base']['poiid'].strip()
            s['name'] = j['base']['name']


            s['parent'] =  j['base']['geodata']['aoi'][0]['mainpoi'] if ('geodata' in j['base'] and j['base']['geodata']['aoi'] and len(j['base']['geodata']['aoi'])>0) else ""


            s['x'] = j['base']['x']
            s['y'] = j['base']['y']
            s['address'] = j['base']['address']
            s['city'],s['adcode'] = citys[s['id']]
            s['star'] = j['scenic']['level'] if ('scenic' in j and 'level' in j['scenic']  and j['scenic']['level']) else ""
            s['type'] = 'poi'
            s['tag'] = j['base']['new_keytype'].split(";")[-1]
            s['theme'] = j['scenic']['theme'] if ('scenic' in j and 'theme' in j['scenic']  and j['scenic']['theme']) else ""
            s['score'] = j['scenic']['src_star'] if ('scenic' in j and 'src_star' in j['scenic'] and j['scenic']['src_star'])  else "0"
            s['intro'] = j['scenic']['intro'] if ('scenic' in j  and 'intro' in j['scenic'] and ( j['scenic']['intro']))  else ""
            s['special'] = j['scenic']['special'] if ('scenic' in j  and 'special' in j['scenic'] and ( j['scenic']['special']))  else ""
            s['tts'] = j['scenic']['midea_info']['scenic_txt_tts'] if ('scenic' in j  and 'midea_info' in j['scenic'] and 'scenic_txt_tts' in j['scenic']['midea_info'] and  j['scenic']['midea_info']['scenic_txt_tts'] )  else ""
            s['cover'] = j['pic_cover']['url'] if ('pic_cover' in j  and  'url' in j['pic_cover']) else ""
            s['shape'] = j['spec']['mining_shape']['shape'] if ('spec' in j  and  'mining_shape' in j['spec'] and 'shape' in j['spec']['mining_shape'] and  j['spec']['mining_shape']['shape'] ) else ""
            s['zoom'] = j['spec']['mining_shape']['level'] if ('spec' in j  and  'mining_shape' in j['spec'] and 'level' in j['spec']['mining_shape'] and  j['spec']['mining_shape']['level'] ) else "18"
            s['shape_rectangle'] = calc_rectangle(s['shape'])
            if s['parent'] == s['id'] :
                #print ("{0},{1}".format( s['parent'] , s['id']))
                s['parent'] = ''
            if (not s['parent']):
                s['type'] = 'aoi'

            specs.append(s)
        except Exception as e:
            print (e)
    return specs

def uppoi (f_specs,ad):
    #conn = sqlite3.connect(u'db\\bany.db')
    #conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    cur = conn.cursor()

    deletesql = "delete from pois where adcode like '"+ad+"%'"
    cur.executescript(deletesql)
    for l in open(f_specs,'r',encoding='utf-8'):
        j = json.loads(l)

        try:
            sql = '''INSERT INTO pois (_id,parent,name,x,y,city,adcode,type,star,tag,theme,score,shape,shape_rectangle,zoom,cover,special) VALUES (  ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cur.execute(sql,(j['id'],j['parent'],j['name'],j['x'],j['y'],j['city'],j['adcode'],j['type'],j['star'],j['tag'],j['theme'],j['score'],j['shape'],j['shape_rectangle'],j['zoom'],j['cover'],j['special']))
        except Exception as e:
            print (e)
            print (j['name'])

    conn.commit()

    return

def uppoisim (f_specs,ad):
    #conn = sqlite3.connect(u'db\\bany.db')
    #conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    cur = conn.cursor()

    deletesql = "delete from pois where adcode like '"+ad+"%'"
    cur.executescript(deletesql)
    for l in open(f_specs,'r',encoding='utf-8'):
        j = json.loads(l)
        name = j['name'].split('-')[-1] if j['type']=='poi' else j['name']
        shape = 1 if j['shape'] else 0


        try:
            sql = '''INSERT INTO pois (_id,parent,name,x,y,city,adcode,type,star,tag,theme,score,shape,zoom,cover) VALUES ( ?, ?, ?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            cur.execute(sql,(j['id'],j['parent'],name,j['x'],j['y'],j['city'],j['adcode'],j['type'],j['star'],j['tag'],j['theme'],j['score'],shape,j['zoom'],j['cover']))
        except Exception as e:
            print (e)
            print (sql)
            print(j)

        if j['shape'] :
            try:
                sql = '''INSERT INTO shape (_id,shape,rectangle) VALUES (  ?, ?, ?)'''
                cur.execute(sql,(j['id'],j['shape'],j['shape_rectangle']))
            except Exception as e:
                print (e)
                print (sql)
                print(j)


    conn.commit()

    return


def upevals (f_pick):
#    conn = sqlite3.connect(u'db\\bany.db')
    #conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    cur = conn.cursor()

    for l in open(f_pick,'r',encoding='utf-8'):
        j = json.loads(l)
        s = {}
        s['id'] = j['base']['poiid'].strip()
        s['name'] = j['base']['name']
        s['parent'] =  j['base']['geodata']['aoi'][0]['mainpoi'] if ('geodata' in j['base'] and j['base']['geodata']['aoi'] and len(j['base']['geodata']['aoi'])>0) else ""
        if s['parent'] == s['id'] :
            #print ("{0},{1}".format( s['parent'] , s['id']))
            s['parent'] = ''
        s['intro'] = j['scenic']['intro'] if ('scenic' in j  and 'intro' in j['scenic'] and ( j['scenic']['intro']))  else ""
        s['special'] = j['scenic']['special'] if ('scenic' in j  and 'special' in j['scenic'] and ( j['scenic']['special']))  else ""
        s['tts'] = j['scenic']['midea_info']['scenic_txt_tts'] if ('scenic' in j  and 'midea_info' in j['scenic'] and 'scenic_txt_tts' in j['scenic']['midea_info'] and  j['scenic']['midea_info']['scenic_txt_tts'] )  else ""
        s['star'] = j['scenic']['level'] if ('scenic' in j and 'level' in j['scenic']  and j['scenic']['level']) else ""
        s['type'] = j['base']['new_keytype'].split(";")[-1]
        s['theme'] = j['scenic']['theme'] if ('scenic' in j and 'theme' in j['scenic']  and j['scenic']['theme']) else ""

        s['pic'] = []
        if 'pic' in j:
            for p in j['pic']:
                #print (p['url'])
                if p['url'] not in s['pic']:
                    s['pic'].append(p['url'])

        text = s['tts'] +"."+s['intro']
        tag = s['star'] +" " + s['type']
        if len(text) > 5 and len(s['pic']) > 0 :
            try:

                sql = '''INSERT INTO evals (poiid,parent,name,tag,text,pic) VALUES (  ?, ?, ?,?, ?, ?)'''
                cur.execute(sql,(s['id'],s['parent'],s['name'],tag,text,json.dumps(s['pic'],ensure_ascii=False)))
            except Exception as e:
                print (e)
                print (s['name'])

    conn.commit()


    return

def level():
    #conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    #conn = sqlite3.connect(u'db\\bany.db')
    cur = conn.cursor()
    for zoom in range(4, 20):
        print (zoom)
        points = []
        sql = "SELECT *  from pois where type='aoi' and show="+str(zoom)+" order by star desc, score desc,tag "
        cursor  = cur.execute(sql).fetchall()
        wf = open("level\\level_"+str(zoom)+".txt",'w',encoding='utf-8')
        wf.writelines("[")
        for row in cursor:
            o = {}
            o['longitude'] = row[4]
            o['latitude'] = row[5]
            o['title'] = row[2]
            o['subtitle'] = row[7]
            o['customID'] = row[0]
            wf.write(json.dumps(o,ensure_ascii = False)+",\n")
        wf.writelines("]")
        wf.close()
        conn.commit()

def crtable():
    cur = conn.cursor()
    create_table_intro ='''
    create table IF NOT EXISTS intro (
        _id         INTEGER PRIMARY KEY autoincrement,
        poiid       TEXT,
        scode       TEXT,
        type        TEXT,
        media       TEXT,
        time        TEXT,
        weather     TEXT,
        content     TEXT,
        url         TEXT
    );
    '''
    cur.executescript(create_table_intro)

    create_table_shape ='''
    create table IF NOT EXISTS shape (
        _id     TEXT NOT NULL PRIMARY KEY,
        shape       TEXT,
        rectangle   TEXT
    );
    '''
    cur.executescript(create_table_shape)

    create_table_pois = '''
    CREATE TABLE  IF NOT EXISTS pois (
        _id     TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        name    TEXT,
        alias   TEXT,
        x       REAL,
        y       REAL,
        city    TEXT,
        adcode  TEXT,
        type    TEXT,
        star    TEXT,
        tag     TEXT,
        theme   TEXT,
        score   REAL,
        shape   INTEGER,
        zoom    INTEGER,
        show    INTEGER,
        cover   TEXT,
        intro TEXT
    );

    '''
    cur.executescript(create_table_pois)




def uptemp():
    cur = conn.cursor()


    points = []
    sql = "select * from evals where  text like '%燕京%'"
    cursor  = cur.execute(sql).fetchall()
    wf = open("evals_yanjing.txt",'w',encoding='utf-8')
    wf.writelines("[")
    for row in cursor:
        wf.write(json.dumps(row,ensure_ascii = False)+",\n")
    wf.writelines("]")
    wf.close()
    conn.commit()


if __name__ == '__main__':
    conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    #conn = sqlite3.connect(u'db\\bany.db')
    crtable()
    adcodes = ["34","11","44","41","15","23","65","42","21","37","32","61","31","52","50","54","35","43","46","63","45","64","36","33","13","71","81","82","62","51","22","12","53","14"]


    for ad in adcodes:
        print (ad+"0000")

        a = pick('raw\\'+ad+'0000_scenic_raw.json')
        b = spec(a['pickpoi'],ad)
        wf = open('pick\\'+ad+"0000_spec.json",'w',encoding='utf-8')
        for j in b:
             wf.write(json.dumps(j,ensure_ascii = False)+"\n")
        wf.close()

        for key in a:
            print ("{0}:{1}".format(key,len(a[key])))
            wf = open('pick\\'+ad+"0000_"+key+".json",'w',encoding='utf-8')
            for j in a[key]:
                wf.write(json.dumps(j,ensure_ascii = False)+"\n")

            wf.close()

        uppoisim("pick\\"+ad+"0000_spec.json",ad)
        #upevals("pick\\"+ad+"0000_pickpoi.json")

    conn.close()











