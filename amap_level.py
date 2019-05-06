#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      Administrator
#
# Created:     04/04/2019
# Copyright:   (c) Administrator 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import json
import sqlite3

from math import radians, cos, sin, asin, sqrt

#公式计算两点间距离（m）

def geodistance(lng1,lat1,lng2,lat2):
    #lng1,lat1,lng2,lat2 = (120.12802999999997,30.28708,115.86572000000001,28.7427)
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
    distance=round(distance,0)
    return distance

def outmappoint(zoom,zoompoints):
    conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
    cur = conn.cursor()
    wf = open("level\\level_"+str(zoom)+".txt",'w',encoding='utf-8')
    wf.writelines("[")
    for l in zoompoints:
        if l['maplevel'] == zoom:
            o = {}
            o['longitude'] = l['x']
            o['latitude'] = l['y']
            o['title'] = l['name']
            o['subtitle'] = l['adcode']
            o['customID'] = l['_id']
            wf.write(json.dumps(o,ensure_ascii = False)+",\n")
            sql = "update pois set show="+str(zoom)+" where _id = '"+l['_id']+"'"
            cur.execute(sql)
    conn.commit()
    conn.close()

    wf.writelines("]")
    wf.close


print(geodistance(118.160062,30.144661,119.762116,40.009852))

SCALE = [5000000, 2000000, 1000000, 500000, 200000, 100000, 50000, 25000, 20000, 10000, 5000, 2000, 1000, 500, 200, 100, 50, 25, 10, 5]


points = []
zoompoints = []
conn = sqlite3.connect(u'E:\\APICloud\\bany\\res\\bany.db')
cur = conn.cursor()
sql = "SELECT *  from pois where type='aoi' and star like 'A%' order by star desc, score desc,tag "
cursor  = cur.execute(sql).fetchall()
for row in cursor:
    points.append({'_id':row[0],'name':row[2],'x':row[4],'y':row[5],'adcode':row[7],'star':row[9]})

for zoom in range(4, 13):
    print (zoom)
    for i in range(len(points)):
        if (not zoompoints) :
            points[i]['maplevel'] = zoom
            zoompoints.append(points[i])
        if  len(zoompoints) >= 2 ** zoom :
            break
        if 'maplevel' in points[i]:
            continue
        if zoom <= 7 and points[i]['star']=='AAAA':
            continue

        if zoom == 7 and points[i]['star']=='AAAAA' and ('maplevel' not in points[i]) :
            points[i]['maplevel'] = zoom
            zoompoints.append(points[i])
            continue

        if zoom == 12 and ('maplevel' not in points[i]) :
            points[i]['maplevel'] = zoom
            zoompoints.append(points[i])
            continue

        flag = True
        for m in zoompoints:

            distance = geodistance(points[i]['x'],points[i]['y'],m['x'],m['y'])
            #print(distance)
            #处理5A景点

            if distance < SCALE[zoom-1]:
                flag = False
                break

        if flag:
            points[i]['maplevel'] = zoom
            zoompoints.append(points[i])


    outmappoint(zoom,zoompoints)








'''
a =  "118.224876,30.106819;118.224406,30.10641;118.224084,30.106498;118.223675,30.106123;118.223389,30.105729;118.223277,30.105496;118.223225,30.105318;118.223205,30.105113;118.223238,30.104721;118.223293,30.104339;118.223414,30.103518;118.223536,30.102679;118.22357,30.102351;118.223604,30.101958;118.22359,30.10184;118.223529,30.10176;118.223396,30.101719;118.223158,30.101666;118.222947,30.101653;118.222729,30.101675;118.222564,30.101743;118.22235,30.101834;118.221444,30.102281;118.220998,30.102493;118.220714,30.102546;118.220434,30.102524;118.219718,30.102505;118.218984,30.102416;118.218895,30.102332;118.218661,30.10217;118.218456,30.102028;118.218035,30.10164;118.217216,30.100938;118.215583,30.099593;118.214872,30.098946;118.214622,30.098763;118.211462,30.096945;118.210575,30.09644;118.210124,30.096082;118.209175,30.095144;118.207519,30.09349;118.207438,30.093408;118.207033,30.093019;118.206731,30.092696;118.206128,30.092199;118.205736,30.091988;118.204723,30.091496;118.204457,30.091317;118.204073,30.091009;118.203625,30.090619;118.203513,30.090506;118.203428,30.090365;118.20294,30.089358;118.202873,30.089282;118.202818,30.089235;118.202748,30.089211;118.202696,30.089213;118.202649,30.089205;118.20262,30.089233;118.202597,30.089266;118.202595,30.089299;118.202599,30.089371;118.202633,30.08943;118.202874,30.089934;118.202969,30.090242;118.202967,30.090345;118.202908,30.090406;118.20283,30.090432;118.202726,30.090424;118.202632,30.09038;118.202419,30.090058;118.201701,30.088997;118.20128,30.088263;118.200164,30.087734;118.199552,30.086922;118.199475,30.086317;118.199289,30.085852;118.19881,30.085466;118.19843,30.08524;118.197938,30.085126;118.197612,30.085112;118.197468,30.085089;118.196513,30.084267;118.195471,30.083417;118.19414,30.082116;118.193554,30.081477;118.193417,30.081334;118.192186,30.080644;118.191905,30.080523;118.191291,30.080357;118.190806,30.080271;118.190612,30.080243;118.190482,30.080168;118.19049,30.080021;118.190547,30.079853;118.190625,30.079667;118.190658,30.079455;118.19059,30.079258;118.190343,30.079018;118.189092,30.07827;118.188726,30.078167;118.188297,30.078083;118.188074,30.077947;118.187933,30.077697;118.182873,30.080926;118.168607,30.089936;118.162442,30.097025;118.154885,30.10297;118.133293,30.105209;118.131099,30.106111;118.113222,30.123108;118.106345,30.134211;118.099467,30.144719;118.092664,30.152678;118.089466,30.155738;118.0788,30.16262;118.077748,30.163416;118.077734,30.164347;118.077722,30.165224;118.078894,30.167068;118.084117,30.170681;118.085265,30.171696;118.092324,30.177447;118.096625,30.180804;118.099163,30.183448;118.100326,30.18431;118.102084,30.185275;118.132593,30.19926;118.134745,30.200124;118.136324,30.20044;118.137302,30.20046;118.14519,30.200294;118.150056,30.200378;118.152776,30.200389;118.153999,30.199924;118.160285,30.196196;118.174858,30.191172;118.198727,30.182469;118.19883,30.182452;118.204611,30.180733;118.208246,30.178642;118.209256,30.176483;118.210867,30.157701;118.212685,30.14953;118.217942,30.135796;118.218275,30.135099;118.218725,30.134598;118.21898,30.134549;118.219299,30.134528;118.219937,30.134573;118.220194,30.134589;118.220516,30.134558;118.220965,30.134448;118.221221,30.13432;118.221315,30.13424;118.221506,30.134066;118.222166,30.133524;118.222841,30.132968;118.223495,30.132456;118.223876,30.132121;118.224176,30.131831;118.224289,30.13161;118.224413,30.13125;118.224585,30.131019;118.224805,30.130783;118.224881,30.130655;118.224944,30.130412;118.225007,30.130196;118.225262,30.129758;118.225597,30.129218;118.22577,30.129091;118.225975,30.128993;118.226142,30.12895;118.226342,30.12893;118.22659,30.128977;118.226896,30.129042;118.227209,30.129068;118.227584,30.129051;118.227848,30.128979;118.227998,30.128885;118.228068,30.128779;118.228192,30.128639;118.228546,30.128453;118.229038,30.128308;118.229587,30.128154;118.22991,30.128056;118.230157,30.127957;118.230426,30.127802;118.230831,30.127475;118.230979,30.127339;118.231099,30.127216;118.231199,30.12715;118.231453,30.127033;118.231756,30.12694;118.232426,30.126588;118.232704,30.126364;118.232755,30.126057;118.232614,30.125733;118.232694,30.12533;118.232712,30.12511;118.23255,30.124888;118.231718,30.124054;118.231731,30.123804;118.231952,30.123716;118.231354,30.122744;118.231141,30.122378;118.230477,30.121054;118.229984,30.119761;118.229834,30.119656;118.229693,30.11949;118.229218,30.119291;118.2287,30.119054;118.227707,30.11873;118.227187,30.118234;118.226796,30.117664;118.226554,30.117104;118.225529,30.115041;118.225317,30.114795;118.22529,30.114536;118.225259,30.114079;118.225262,30.113666;118.225132,30.113487;118.224973,30.113358;118.224856,30.113293;118.224794,30.113189;118.224659,30.112127;118.224634,30.111958;118.224632,30.111912;118.224745,30.11186;118.224893,30.111713;118.225074,30.111531;118.225246,30.111319;118.225293,30.111142;118.225253,30.110837;118.225178,30.110736;118.225087,30.110643;118.224973,30.110554;118.224916,30.110452;118.224811,30.109868;118.224701,30.10942;118.224666,30.109108;118.224696,30.108937;118.225008,30.10814;118.225184,30.107598;118.225189,30.107405;118.225118,30.107158;118.224876,30.106819"
b = a.split(";")
lng_min,lat_min,lng_max,lat_max =['','','',''];
for s in b:
    a,b = s.split(',')
    lng_min = a if lng_min else ""
    if (a < lng_min or not lng_min ): lng_min = a
    if (a > lng_max or not lng_max): lng_max = a
    if b < lat_min or  not lat_min: lat_min = b
    if b > lat_max or not lat_max : lat_max = b
print('{0},{1};{2},{3}'.format(lng_min,lat_min,lng_max,lat_max))


adcode = []
wf = open("adcode_mini.txt",'w',encoding='utf-8')
for l in open('adcode_polyline.txt','r',encoding='utf-8'):
    j = json.loads(l)
    print (j['adcode'])
    ro = {}
    ro['name'] = j['name']
    ro['lon'] = j['center'].split(',')[0]
    ro['lat'] = j['center'].split(',')[1]
    ro['polyline'] = []

    polyline = j['polyline'].split(';')
    lenp = len(polyline)
    if lenp > 10000:
        dep = 50
    elif lenp > 3000:
        dep = 30
    elif lenp > 1000:
        dep = 5
    elif lenp < 300:
        dep = 1
    else:
        dep = 2
    for i in range(len(polyline)):
        if i % dep == 0  or i == len(polyline)-1 :
            ro['polyline'].append({'lon': polyline[i].split(',')[0] ,'lat': polyline[i].split(',')[1] })
    print (len(ro['polyline']))
    wf.write(json.dumps(ro,ensure_ascii = False)+",\n")
wf.close()


'''




