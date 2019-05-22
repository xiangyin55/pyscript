#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      Administrator
#
# Created:     07/05/2019
# Copyright:   (c) Administrator 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sqlite3
import json
import logger
import time

log_name=time.strftime("db-%Y-%m-%d.log", time.localtime())
dblog = logger.logger("debug",log_name=log_name)

if 'dbpath' not in locals().keys() : dbpath = u'db\\mfw.db'


def t_c ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    create_table_poi ='''
    create table IF NOT EXISTS poi (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        mdd     TEXT,
        level   INTEGER,
        name    TEXT,
        text    TEXT,
        aid     TEXT,
        amap    TEXT,
        flag    INTEGER  default 0
    );
    '''
    cur.executescript(create_table_poi)

    create_table_mdd ='''
    create table IF NOT EXISTS mdd (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        level   INTEGER,
        name    TEXT,
        text    TEXT,
        flag     INTEGER  default 0
    );
    '''
    cur.executescript(create_table_mdd)

    create_table_img ='''
    create table IF NOT EXISTS img (
        pid     TEXT NOT NULL PRIMARY KEY,
        poi     TEXT,
        aid     TEXT,
        name    TEXT,
        url     TEXT,
        direct  INTEGER  default 0,
        year    INTEGER  default 2018,
        mon     INTEGER  default 1,
        day     INTEGER  default 1,
        flag    INTEGER  default 0
    );
    '''
    cur.executescript(create_table_img)


    conn.commit()
    conn.close()
    return

def t_poi_a (res):
    if not res : return
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sucs = True
    for r in res:
        try:
            sql = 'INSERT INTO poi (id,parent,mdd,level,name) VALUES ( "{}","{}","{}",{},"{}" )'.format(r['id'],r['parent'],r['mdd'],r['level'],r['name'])
            cur.execute(sql)

        except Exception as e:
            try:
                if not r['mdd']:
                    sql = 'UPDATE poi SET parent="{}", level={}, name="{}" WHERE id="{}"'.format(r['parent'],r['level'],r['name'],r['id'])
                else:
                    sql = 'UPDATE poi SET parent="{}", mdd="{}", level={}, name="{}" WHERE id="{}"'.format(r['parent'],r['mdd'],r['level'],r['name'],r['id'])
                cur.execute(sql)
            except Exception as e:
                dblog.warning(e)
                sucs = False
            else:
                i = 0
                #print (sql +" is OK!")
        dblog.debug (sql)
    if sucs and res[0]['parent'] :
        try:
            id = res[0]['parent']
            sql = 'UPDATE poi SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            dblog.warning(e)
        dblog.debug (sql)

    elif sucs and res[0]['mdd'] :
        try:
            id = res[0]['mdd']
            sql = 'UPDATE mdd SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            dblog.warning(e)
        dblog.debug (sql)

    conn.commit()
    conn.close()
    return



def t_poi_u(id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE poi SET flag=2  WHERE id="{}"'.format(id)
        cur.execute(sql)
    except Exception as e:
        dblog.warning(e)
    dblog.debug (sql)
    conn.commit()
    conn.close()

def t_poi_u_t(id,text):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = "UPDATE poi SET text=?  WHERE id=?"
        cur.execute(sql,(text,id))
    except Exception as e:
        dblog.warning(e)
    dblog.debug (sql)
    conn.commit()
    conn.close()

def t_poi_u_a(aid,text,id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = "UPDATE poi SET aid=? ,amap=? WHERE id=?"
        cur.execute(sql,(aid,text,id))
    except Exception as e:
        dblog.warning(e)
    dblog.debug (sql)
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
        dblog.warning(e)
        cursor = ""
    dblog.debug (sql)
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
        dblog.warning(e)
        cursor = ""
    dblog.debug (sql)
    conn.commit()
    conn.close()
    return cursor


def t_mdd_a (res):
    if not res : return

    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sucs = True
    for r in res:

        try:
            sql = 'INSERT INTO mdd (id,parent,level,name) VALUES ( "{}","{}",{},"{}" )'.format(r['id'],r['parent'],r['level'],r['name'])
            cur.execute(sql)
        except :
            try:
                sql = 'UPDATE mdd SET parent="{}", level={}, name="{}" WHERE id="{}"'.format(r['parent'],r['level'],r['name'],r['id'])
                cur.execute(sql)
            except Exception as e:
                dblog.warning(e)
                sucs = False
        if ldebug :print (sql)

    if sucs and res[0]['parent'] :
        try:
            id = res[0]['parent']
            sql = 'UPDATE mdd SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            dblog.warning(e)
        if ldebug :print (sql)

    conn.commit()
    conn.close()
    return

def t_mdd_s (level=2):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        if level == 1:
            sql = 'SELECT id  from mdd where level=1 and flag=0'
        else:
            sql = 'SELECT id  from mdd where (level=2 and flag=0) or flag=0'
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        dblog.warning(e)
        cursor = ""
    if ldebug :print (sql)
    conn.commit()
    conn.close()
    return cursor

def t_mdd_u(id):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE mdd SET flag=2  WHERE id="{}"'.format(id)
        cur.execute(sql)
    except Exception as e:
        dblog.warning(e)
    dblog.debug (sql)
    conn.commit()
    conn.close()



def t_img_s ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'select id,aid from poi where amap!="" and pic=""'
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        dblog.warning(e)
        cursor = ""
    dblog.debug (sql)
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
        dblog.warning(e)
    dblog.debug (sql)
    conn.commit()
    conn.close()
    return


def t_img_a (res):
    if not res : return

    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sucs = True
    for r in res:
        try:
            sql = 'INSERT INTO img (pid,poi,aid,name,url,direct,year,mon,day) VALUES ( "{}","{}","{}","{}","{}",{},{},{},{} )'.format(r['pid'],r['poi'],r['aid'],r['name'],r['url'],r['direct'],r['y'],r['m'],r['d'])
            cur.execute(sql)
        except Exception as e:
            sucs = False
            dblog.warning(e)
        dblog.debug (sql)

    id = res[0]['poi']

    if sucs and id :
        try:
            sql = 'UPDATE poi SET pic="1"  WHERE id="{}"'.format(id)
            cur.execute(sql)
        except Exception as e:
            dblog.warning(e)
    if not sucs:
        try:
            sql = 'Delete from img WHERE poi="{}"'.format(id)
            cur.execute(sql)
        except Exception as e:
            dblog.warning(e)
    dblog.debug (sql)


    conn.commit()
    conn.close()
    return

