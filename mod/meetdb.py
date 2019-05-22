# -*- encoding: utf-8 -*-

import sqlite3
import json
import mod.logger as logger
import time



if  not 'log' in locals().keys() :
    log_name=time.strftime("db-%Y-%m-%d.log", time.localtime())
    log = logger.logger("info",log_name=log_name)

if 'dbpath' not in locals().keys() : dbpath = u'db\\meet.db'

def bsql(t,o,mode='i'):

    sql = ''
    if mode == 'i':
        k,v = '',''
        for item in o:
            s = '"'+o[item]+'"'
            k += item if not k else ','+item
            v += s if not v else ','+s
        sql = 'INSERT INTO {} ({}) VALUES ( {} )'.format(t,k,v)

    elif mode == 'u':
        s = ''
        for item in o:
            if item =='id': continue
            s += ',' if s else ''
            if isinstance(o[item],int):
                s += "{}={}".format(item,str(o[item]))
            else:
                s += "{}='{}'".format(item,o[item].replace("'","''"))

        sql = 'UPDATE {} SET {} WHERE id="{}"'.format(t,s,o['id'])
    #log.debug(sql)
    return sql



def t_c ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()


    create_table_mdd ='''
    create table IF NOT EXISTS mdd (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        name    TEXT,
        level   INTEGER,
        count   INTEGER default 0,
        sub     INTEGER default 0,
        flag    INTEGER  default 0,
        subflag    INTEGER  default 0
    );
    '''
    cur.executescript(create_table_mdd)

    create_table_poi ='''
    create table IF NOT EXISTS poi (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        name    TEXT,
        mdd     TEXT,
        area     TEXT,
        level   INTEGER,
        star    TEXT,
        type    TEXT,
        img     TEXT,
        nav     TEXT,
        line     TEXT,
        text    TEXT,
        sub     TEXT,
        want    INTEGER default 0,
        gone    INTEGER default 0,
        sort    INTEGER default 0,
        flag    INTEGER default 0
    );
    '''
    cur.executescript(create_table_poi)


    create_table_scenic ='''
    create table IF NOT EXISTS scenic (
        id      TEXT NOT NULL PRIMARY KEY,
        poi     TEXT,
        name    TEXT,
        type    TEXT,
        url     TEXT,
        text    TEXT,
        year    INTEGER  default 2018,
        mon     INTEGER  default 1,
        day     INTEGER  default 1,
        flag    INTEGER  default 0
    );
    '''
    cur.executescript(create_table_scenic)


    conn.commit()
    conn.close()
    return

def t_s (s):

    jsql = {
        'mdd': 'SELECT id  from mdd where sub=1 and flag=0',
        'aoi': 'SELECT id  from mdd where subflag=0',
        'down' : 'SELECT id  from poi where flag=0 order by star desc',
        'poi' : 'SELECT id  from poi where flag=1 order by star desc'
        }

    if not s in jsql:
        log.error('{} is not in select sql list!'.format(s))

        return -1


    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()


    try:
        sql = jsql[s]
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        log.warning(e)
        cursor = ""
    log.debug (sql)
    conn.commit()
    conn.close()
    return cursor





def t_poi_u(id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE poi SET flag=2  WHERE id="{}"'.format(id)
        cur.execute(sql)
    except Exception as e:
        log.warning(e)
    log.debug (sql)
    conn.commit()
    conn.close()

def t_poi_u_t(id,text):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = "UPDATE poi SET text=?  WHERE id=?"
        cur.execute(sql,(text,id))
    except Exception as e:
        log.warning(e)
    log.debug (sql)
    conn.commit()
    conn.close()

def t_poi_u_a(aid,text,id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = "UPDATE poi SET aid=? ,amap=? WHERE id=?"
        cur.execute(sql,(aid,text,id))
    except Exception as e:
        log.warning(e)
    log.debug (sql+";"+text)
    conn.commit()
    conn.close()

def t_poi_s (level=None):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    if not level:
        sql = 'SELECT id from poi where text is NULL'
    else:
        sql = 'SELECT id  from poi where level={0} and flag=0'.format(level)
    try:
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        log.warning(e)
        cursor = ""
    log.debug (sql)
    conn.commit()
    conn.close()
    return cursor

def t_poi_s_t ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sql = 'SELECT text from poi where text is not NULL and (aid = "" or aid is null)'
    try:
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        log.warning(e)
        cursor = ""
    log.debug (sql)
    conn.commit()
    conn.close()
    return cursor



def t_img_s ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'select id,aid from poi where amap!="" and pic=""'
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        log.warning(e)
        cursor = ""
    log.debug (sql)
    conn.commit()
    conn.close()
    return cursor

def t_img_a_p (id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE poi SET pic="2"  WHERE id="{}"'.format(id)
        cur.execute(sql)
    except Exception as e:
        log.warning(e)
    log.debug (sql)
    conn.commit()
    conn.close()
    return


def t_img_a (res):
    if not res : return


    sucs = True
    for r in res:
        try:
            sql = 'INSERT INTO img (pid,poi,aid,name,url,direct,year,mon,day) VALUES ( "{}","{}","{}","{}","{}",{},{},{},{} )'.format(r['pid'],r['poi'],r['aid'],r['name'],r['url'],r['direct'],r['y'],r['m'],r['d'])
            cur.execute(sql)
        except Exception as e:
            sucs = False
            log.warning(e)
        log.debug (sql)

    id = res[0]['poi']

    if sucs and id :
        try:
            sql = 'UPDATE poi SET pic="1"  WHERE id="{}"'.format(id)
            cur.execute(sql)
        except Exception as e:
            log.warning(e)
    if not sucs:
        try:
            sql = 'Delete from img WHERE poi="{}"'.format(id)
            cur.execute(sql)
        except Exception as e:
            log.warning(e)
    log.debug (sql)


    conn.commit()
    conn.close()
    return




def t_mdd_a (res):
    if not res : return

    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sucs = True
    for r in res:

        try:
            sql = 'INSERT INTO mdd (id,parent,name,count,sub) VALUES ( "{}","{}","{}",{},{} )'.format(r['id'],r['parent'],r['name'],r['count'],r['sub'])
            cur.execute(sql)
        except :
            try:
                sql = 'UPDATE mdd SET parent="{}",name="{}",count={},sub={} WHERE id="{}"'.format(r['parent'],r['name'],r['count'],r['sub'],r['id'])
                cur.execute(sql)
            except Exception as e:
                log.warning(e)
                sucs = False
        log.debug (sql)

    conn.commit()
    conn.close()
    return

def t_mdd_s (s='mdd'):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    if s=='mdd':
        sql = 'SELECT id  from mdd where sub=1 and flag=0'
    else :
        sql = 'SELECT id  from mdd where subflag=0'


    try:
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        log.warning(e)
        cursor = ""
    log.debug (sql)
    conn.commit()
    conn.close()
    return cursor

def t_mdd_u(id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE mdd SET flag=1  WHERE id="{}"'.format(id)
        cur.execute(sql)
    except Exception as e:
        log.warning(e)
    log.debug (sql)
    conn.commit()
    conn.close()



def opendb():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    return conn,cur

def closedb(conn):
    conn.commit()
    conn.close()


def t_mdd_update(o):
    conn,cur = opendb()
    try:
        sql = bsql('mdd',o,'u')
        cur.execute(sql)
    except Exception as e:
        log.warning(e)
    log.info(sql)

    closedb(conn)

def t_poi_append (res):
    if not res : return
    conn,cur = opendb()
    sucs = True
    for r in res:
        try:
            sql = bsql('poi',r,'i')
            cur.execute(sql)

        except Exception as e:
            try:
                sql = bsql('poi',r,'u')
                cur.execute(sql)
            except Exception as e:
                log.warning(e)
                sucs = False
                break
            else:
                i = 0
                #print (sql +" is OK!")
    log.info(sql)
    closedb(conn)
    return sucs

def t_poi_update (res):

    if not res : return
    conn,cur = opendb()

    for r in res:
        sql = bsql('poi',r,'u')
        try:
            cur.execute(sql)
        except Exception as e:

            log.warning(e)
        log.debug(sql)
    closedb(conn)

    return