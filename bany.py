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


import json,time,re,random
import mod.db as db
import mod.amap as amap
import mod.common as common
import mod.logger as logger




SCALE = [5000000, 2000000, 1000000, 500000, 200000, 100000, 50000, 25000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5]

log = logger.logger("info",log_name=time.strftime("bany-%Y-%m-%d.log", time.localtime()))
bany = db.database('dat\\bany.db')
m = amap.amap()

def district():
    ids = []
    dists = []


    ss =  m.district('100000',3)
        # 仅仅添加第三级，其他级别不添加
    for p in ss['districts'][0]['districts']:
        if p['adcode'] not in ids:
            ids.append(p['adcode'])
            dists.append({'id':p['adcode'],'name':p['name']})


        for l in p['districts']:
            if l['adcode'] not in ids: #取省份
                    ids.append(l['adcode'])
                    dists.append({'id':l['adcode'],'area':l['citycode'],'name':l['name']})

            for m in l['districts']:
                if m['adcode'] not in ids :   #取省份
                    ids.append(m['adcode'])
                    dists.append({'id':m['adcode'],'area':m['citycode'],'name':m['name']})

    log.info('found {} district!'.format(len(dists)))
    return bany.t_a('district',dists,1)

def category():
    res =  [
      { "class" : "build", "id" : "世界遗产" },
      { "class" : "build", "id" : "国家级景点" },
      { "class" : "build", "id" : "风景名胜" },
      { "class" : "build", "id" : "旅游景点" },
      { "class" : "build", "id" : "观景点" },
      { "class" : "build", "id" : "海滩" },
      { "class" : "build", "id" : "公园广场" },
      { "class" : "build", "id" : "动物园" },
      { "class" : "build", "id" : "植物园" },
      { "class" : "build", "id" : "水族馆" },
      { "class" : "build", "id" : "纪念馆" },
      { "class" : "build", "id" : "寺庙道观" },
      { "class" : "build", "id" : "教堂" },
      { "class" : "build", "id" : "回教寺" },
      { "class" : "build", "id" : "旅游设施" },
      { "class"  : "honor" , "id" : "世界自然遗产" },
      { "class"  : "honor" , "id" : "世界文化遗产" },
      { "class"  : "honor" , "id" : "世界文化景观遗产" },
      { "class"  : "honor" , "id" : "世界文化与自然双重遗产" },
      { "class"  : "honor" , "id" : "国家AAAAA级旅游景区" },
      { "class"  : "honor" , "id" : "国家AAAA级旅游景区" },
      { "class"  : "honor" , "id" : "国家AAA级旅游景区" },
      { "class"  : "honor" , "id" : "国家AA级旅游景区" },
      { "class"  : "honor" , "id" : "国家A级旅游景区" },
      { "class"  : "honor" , "id" : "国家重点文物保护单位" },
      { "class"  : "honor" , "id" : "国家级森林公园" },
      { "class"  : "honor" , "id" : "国家级湿地公园" },
      { "class"  : "honor" , "id" : "国家级风景名胜区" },
      { "class"  : "honor" , "id" : "国家级自然保护区" },
      { "class"  : "honor" , "id" : "国家水利风景区" },
      { "class"  : "honor" , "id" : "国家地质公园" },
      { "class"  : "honor" , "id" : "爱国主义教育基地" },
      { "class"  : "honor" , "id" : "文化旅游景点" },
      { "class"  : "honor" , "id" : "科普教育基地" },
      { "class"  : "honor" , "id" : "红色旅游景区" },
      { "class"  : "honor" , "id" : "文物保护单位" },
      { "class"  : "honor" , "id" : "国防教育基地" },
      { "class"  : "honor" , "id" : "自然保护区" },
      { "class" : "tour", "id" : "宗教文化游" },
      { "class" : "tour", "id" : "自然景观游" },
      { "class" : "tour", "id" : "草原游" },
      { "class" : "tour", "id" : "森林景观游" },
      { "class" : "tour", "id" : "文化游" },
      { "class" : "tour", "id" : "古迹游" },
      { "class" : "tour", "id" : "古镇游" },
      { "class" : "tour", "id" : "工业游" },
      { "class" : "tour", "id" : "红色游" },
      { "class" : "tour", "id" : "生态游" },
      { "class" : "tour", "id" : "农业游" },
      { "class" : "tour", "id" : "建筑景观游" },
      { "class" : "tour", "id" : "历史文化游" },
      { "class" : "tour", "id" : "名人游" },
      { "class" : "tour", "id" : "历史游" },
      { "class" : "tour", "id" : "民俗游" },
      { "class" : "tour", "id" : "山水游" },
      { "class" : "tour", "id" : "人文游" },
      { "class" : "tour", "id" : "溶洞景观游" },
      { "class" : "tour", "id" : "民族游" },
      { "class" : "tour", "id" : "周末游" },
      { "class" : "tour", "id" : "湖泊景观游" },
      { "class" : "tour", "id" : "森林游" },
      { "class" : "tour", "id" : "宗教游" },
      { "class" : "tour", "id" : "民俗风情游" },
      { "class" : "tour", "id" : "温泉休闲游" },
      { "class" : "tour", "id" : "科普文化游" },
      { "class" : "tour", "id" : "园林景观游" },
      { "class" : "tour", "id" : "艺术游" },
      { "class" : "tour", "id" : "自驾游" },
      { "class" : "tour", "id" : "边境游" },
      { "class" : "tour", "id" : "雪山景观游" },
      { "class" : "tour", "id" : "园林文化游" },
      { "class" : "tour", "id" : "革命文化游" },
      { "class" : "tour", "id" : "民俗文化游" },
      { "class" : "tour", "id" : "古建游" },
      { "class" : "tour", "id" : "生态景观游" },
      { "class" : "tour", "id" : "峡谷景观游" },
      { "class" : "tour", "id" : "草原景观游" },
      { "class" : "tour", "id" : "商务游" },
      { "class" : "tour", "id" : "乡村游" },
      { "class" : "tour", "id" : "度假游" },
      { "class" : "tour", "id" : "郊游" },
      { "class" : "tour", "id" : "自然风光游" },
      { "class" : "tour", "id" : "少数民族风情游" },
      { "class" : "tour", "id" : "观光游" },
      { "class" : "tour", "id" : "亲子游" },
      { "class" : "tour", "id" : "温泉游" },
      { "class" : "tour", "id" : "名人文化游" },
      { "class" : "tour", "id" : "海岛游" },
      { "class" : "tour", "id" : "民族风情游" },
      { "class" : "tour", "id" : "校园游" },
      { "class" : "tour", "id" : "温泉景观游" },
      { "class" : "tour", "id" : "爱国游" },
      { "class" : "tour", "id" : "建筑游" },
      { "class" : "tour", "id" : "园林游" },
      { "class" : "tour", "id" : "古村游" },
      { "class" : "tour", "id" : "地质景观游" },
      { "class" : "tour", "id" : "阿胶文化游" },
      { "class" : "tour", "id" : "主题文化游" },
      { "class" : "tour", "id" : "军事文化游" },
      { "class" : "tour", "id" : "家庭游" },
      { "class" : "tour", "id" : "城市游" },
      { "class" : "tour", "id" : "冰雪生态游" },
      { "class" : "tour", "id" : "海洋景观游" },
      { "class" : "tour", "id" : "名著游" },
      { "class" : "tour", "id" : "生态农渔游" },
      { "class" : "tour", "id" : "红酒文化游" },
      { "class" : "tour", "id" : "文学游" },
      { "class" : "tour", "id" : "瀑布景观游" },
      { "class" : "tour", "id" : "春游" },
      { "class" : "tour", "id" : "农业景观游" },
      { "class" : "tour", "id" : "生态观光游" },
      { "class" : "tour", "id" : "夜游" },
      { "class" : "tour", "id" : "陶瓷文化游" },
      { "class" : "tour", "id" : "书法石刻文化游" },
      { "class" : "tour", "id" : "世界风情游" },
      { "class" : "tour", "id" : "佛教文化游" },
      { "class" : "tour", "id" : "红色文化游" },
      { "class" : "tour", "id" : "石雕观光游" },
      { "class" : "tour", "id" : "冰川地貌景观游" },
      { "class" : "tour", "id" : "地貌景观游" },
      { "class" : "tour", "id" : "影视游" },
      { "class" : "tour", "id" : "古建筑游" },
      { "class" : "tour", "id" : "科谱游" },
      { "class" : "tour", "id" : "教育游" },
      { "class" : "tour", "id" : "书法艺术游" },
      { "class" : "tour", "id" : "水利游" },
      { "class" : "tour", "id" : "中国传统文化游" },
      { "class" : "tour", "id" : "瓷器文化游" },
      { "class" : "tour", "id" : "风情游" },
      { "class" : "tour", "id" : "科普游" },
      { "class" : "tour", "id" : "沙漠游" },
      { "class" : "tour", "id" : "地质地貌景观游" },
      { "class" : "tour", "id" : "古城游" },
      { "class" : "tour", "id" : "军事景观游" },
      { "class" : "tour", "id" : "休闲游" },
      { "class" : "tour", "id" : "沙漠景观游" },
      { "class" : "tour", "id" : "历史景观游" },
      { "class" : "tour", "id" : "河流景观游" },
      { "class" : "tour", "id" : "古街游" },
      { "class" : "tour", "id" : "石窟文化游" },
      { "class" : "tour", "id" : "奇石文化游" },
      { "class" : "tour", "id" : "艺术文化游" },
      { "class" : "tour", "id" : "家庭出游" },
      { "class" : "tour", "id" : "冰雪游" },
      { "class" : "tour", "id" : "边界游" },
      { "class" : "tour", "id" : "梯田景观游" },
      { "class" : "tour", "id" : "情侣游" },
      { "class" : "tour", "id" : "湖泊游" },
      { "class" : "tour", "id" : "草原风情游" },
      { "class" : "tour", "id" : "石窟景观游" },
      { "class" : "tour", "id" : "门文化游" },
      { "class" : "tour", "id" : "休闲度假游" },
      { "class" : "tour", "id" : "风光游" },
      { "class" : "tour", "id" : "田园游" },
      { "class" : "tour", "id" : "古村镇游" },
      { "class" : "tour", "id" : "泉水景观游" },
      { "class" : "tour", "id" : "温泉健身游" },
      { "class" : "tour", "id" : "边境风情游" },
      { "class" : "tour", "id" : "火山科考游" },
      { "class" : "tour", "id" : "避暑度假游" },
      { "class" : "tour", "id" : "金秋摄影游" },
      { "class" : "tour", "id" : "冰雪运动游" }
    ]
    return bany.t_a('category',res)


def pick(adcode):

    return picks




def pois(ids,tid=0):
    for ad in ids:
        adcode = ad[0]
        log.info(adcode)
        scenids = []   #挑选前所有的景点数据
        scenics = []   #挑选前所有的景点数据
        pickids = []   #挑选后的景点ID列表
        picks = []     #挑选后的景点数据
        shapes = []
        intros = []
        images = []


        fils =  ['充电站','管理处','暂停营业','建设中','装修中','交口处','导览图','缆车下站','总台','管理班','项目部','自助售卖机','保安亭','调度室']
        f_poi = 'cache\\amap\\'+adcode+'_pois_raw.json'
        f_raw = 'cache\\amap\\'+adcode+'_scenic_raw.json'


        citys = {}
        for l in open(f_poi,'r',encoding='utf-8'):
            j = json.loads(l)
            id = j['id']
            citys[id] = j['cityname'],j['adcode'][0:4]+"00"

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
                log.error (l)
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

        '''
        log.info ("null filter Pickids len is {0}".format(str(len(pickids))))
        at, pickids = pickids, []
        for id in at:
            if id in scenids:
                pickids.append(id)
            else :
                nuaoi.append(id)
                print (id)
        '''
        log.info ("Pickids len is {0}".format(str(len(pickids))))

        for j in scenics:
            try:
                s = {}
                s['id'] = j['base']['poiid'].strip()
                s['name'] = j['base']['name']
                s['parent'] =  j['base']['geodata']['aoi'][0]['mainpoi'] if ('geodata' in j['base'] and j['base']['geodata']['aoi'] and len(j['base']['geodata']['aoi'])>0) else ""
                s['x'] = j['base']['x']
                s['y'] = j['base']['y']
                #s['address'] = j['base']['address']
                if s['id'] in citys:
                    s['city'],s['adcode'] = citys[s['id']]
                s['star'] = j['scenic']['level'] if ('scenic' in j and 'level' in j['scenic']  and j['scenic']['level']) else ""
                s['type'] = 'poi'
                s['tag'] = j['base']['new_keytype'].split(";")[-1]
                s['theme'] = j['scenic']['theme'] if ('scenic' in j and 'theme' in j['scenic']  and j['scenic']['theme']) else ""
                s['score'] = j['scenic']['src_star'] if ('scenic' in j and 'src_star' in j['scenic'] and j['scenic']['src_star'])  else "0"
                s['cover'] = j['pic_cover']['url'] if ('pic_cover' in j  and  'url' in j['pic_cover']) else ""
                s['zoom'] = j['spec']['mining_shape']['level'] if ('spec' in j  and  'mining_shape' in j['spec'] and 'level' in j['spec']['mining_shape'] and  j['spec']['mining_shape']['level'] ) else "18"

                if s['parent'] == s['id'] :
                    s['parent'] = ''
                if (not s['parent']):
                    s['type'] = 'aoi'

                bfil = False
                for fi in fils:
                    if fi in s['name'] : bfil = True

                if (not bfil)  and ( s['id'] in pickids or  s['parent'] in pickids):
                    shape = j['spec']['mining_shape']['shape'] if ('spec' in j  and  'mining_shape' in j['spec'] and 'shape' in j['spec']['mining_shape'] and  j['spec']['mining_shape']['shape'] ) else ""
                    if shape:
                        shapes.append({'id': s['id'],'shape': shape})
                        s['shape'] = 1
                    intro = j['scenic']['intro'] if ('scenic' in j  and 'intro' in j['scenic'] and ( j['scenic']['intro']))  else ""
                    special = j['scenic']['special'] if ('scenic' in j  and 'special' in j['scenic'] and ( j['scenic']['special']))  else ""
                    guide = j['scenic']['midea_info']['scenic_txt_tts'] if ('scenic' in j  and 'midea_info' in j['scenic'] and 'scenic_txt_tts' in j['scenic']['midea_info'] and  j['scenic']['midea_info']['scenic_txt_tts'] )  else ""
                    if intro or special or guide:
                        s['intro'] = "1"

                    s['name'] = s['name'].split("-")[-1]
                    s['name'] = s['name'].split("·")[-1]
                    picks.append(s)

                    if intro:
                        intros.append({'id': s['id']+'_base','poi': s['id'],'parent':s['parent'],'classify':'base','text':intro})
                    if special:
                        intros.append({'id': s['id']+'_special','poi': s['id'],'parent':s['parent'],'classify':'special','text':special})
                    if guide:
                        intros.append({'id': s['id']+'_guide','poi': s['id'],'parent':s['parent'],'classify':'guide','text':guide})
                    pics = []
                    picids = []
                    if 'pic' in j:
                        for p in j['pic']:
                            if p['url'] not in picids:
                                    pics.append({'id':p['url'],'poi': s['id'],'parent':s['parent']})
                                    picids.append(p['url'])

                    images += pics


            except Exception as e:
                log.warning (j)
                log.warning (e)

        bany.t_a('pois',picks,True,True)
        bany.t_a('shape',shapes,True,True)
        bany.t_a('scenic',intros,True,True)
        #open('intros.txt','a',encoding='utf-8') .write(json.dumps(intros).replace("}, {","}, \n{"))

        print (len(images))
        #open('images.txt','a',encoding='utf-8') .write(json.dumps(images).replace("}, {","}, \n{"))
        bany.t_a('image',images,True,True)



        log.debug(len(picks))


    return True







from math import radians, cos, sin, asin, sqrt
def distance(lng1,lat1,lng2,lat2):
    #lng1,lat1,lng2,lat2 = (120.12802999999997,30.28708,115.86572000000001,28.7427)
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
    distance=round(distance,0)
    return distance

def level (ids,tid=0):
    log.info('start function level, process records count is {}'.format(str(len(ids))))
    points = []
    zoompoints = []
    for row in ids:
        points.append({'id':row[0],'name':row[1],'x':row[2],'y':row[3],'adcode':row[4],'star':row[5]})


    for zoom in range(4, 13):
        log.info ('start map zoom at {} level'.format(str(zoom)))
        for i in range(len(points)):
            if (not zoompoints) :
                points[i]['maplevel'] = zoom
                zoompoints.append(points[i])
                continue

            if zoom == 12 and ('maplevel' not in points[i]) :
                points[i]['maplevel'] = zoom
                zoompoints.append(points[i])
                continue

            if 'maplevel' in points[i]:
                continue

            if zoom <= 7 and (points[i]['star']=='AAAA' or points[i]['star']=='AAA'):
                continue

            if zoom == 7 and points[i]['star']=='AAAAA' and ('maplevel' not in points[i]) :
                points[i]['maplevel'] = zoom
                zoompoints.append(points[i])
                continue

            if  len(zoompoints) >= 2 ** zoom :
                break



            flag = True
            for m in zoompoints:

                d = distance(points[i]['x'],points[i]['y'],m['x'],m['y'])
                #print(distance)
                #处理5A景点

                if d < SCALE[zoom-1]:
                    flag = False
                    break

            if flag:
                points[i]['maplevel'] = zoom
                zoompoints.append(points[i])

    log.info('update database, set show field!')
    for m in zoompoints:
        bany.t_u('pois',{'id':m['id'],'show':m['maplevel']})

    log.info('Finish function level, success process records count is {}'.format(str(len(zoompoints))))
    return


def level2f (ids):
    log.info('start function output level file, process records count is {}'.format(str(len(ids))))
    points = {}
    for row in ids:
        if row[6] not in points:
            points[row[6]] = []
        points[row[6]].append({'id':row[0],'name':row[1],'x':row[2],'y':row[3],'adcode':row[4]})
    for key in points:
        wf = open("out\\level_"+str(key)+".txt",'w',encoding='utf-8')
        wf.write(json.dumps(points[key],ensure_ascii = False).replace('}, {','}, \n{').replace('[','[\n').replace(']','\n]'))
        wf.close()



import urllib
from PIL import Image
def filimg(ids,tid=0):
    i = 0
    for id in ids:
        try:
            '''
            response = common.craw(id[0])
            print (response.content)

            if not response:
                bany.t_u('image',{'id':id[0],'flag':-2})
                continue
            im = Image.open(BytesIO().write(response.content))
            break
            '''

            im = Image.open(urllib.request.urlopen(id[0]))
            if im.size:
                x,y = im.size
                if y > x :
                    i += 1
                    log.debug("{},{},{},{} - {}".format(id[0], im.format, im.size, im.mode,str(i)))
                    bany.t_u('image',{'id':id[0],'flag':1})
                else:
                    bany.t_u('image',{'id':id[0],'flag':-1})

        except Exception as e:
            log.warning (e)
            bany.t_u('image',{'id':id[0],'flag':-2})

#from skimage import io

def pickimg (ids,tid=1):
    for id in ids:
        try:

            im = Image.open(urllib.request.urlopen(id[0]))
            im.show()
            s = input()
            print (s)

            '''

            cap = cv2.VideoCapture(id[0])
            if( cap.isOpened() ) :
                ret,img = cap.read()
                cv2.imshow("image",img)
                cv2.waitKey()


            image = io.imread(id[0])
            io.imshow(image)
            io.show()
            break
            '''

        except Exception as e:
            log.warning (e)
            break





if __name__ == '__main__':
    #print(district())
    #print(category())
    #pois(bany.t_s('province'))
    #filimg(['http://store.is.autonavi.com/showpic/31b8ba33a8261e61c9f5e9e0a813200f'])
    #common.threadrun(filimg,bany.t_s('image'),15)
    #filimg(bany.t_s('image'))


    #print(distance(118.160062,30.144661,119.762116,40.009852))
    #dblevel(bany.t_s('level'))
    #level2f(bany.t_s('level'))
    pickimg(bany.t_s('pickimage'))












