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

if 'dbpath' not in locals().keys() : dbpath = u'db\\mfw.db'
if 'ldebug' not in locals().keys() : ldebug = False

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
                if ldebug : print (e)
                sucs = False
            else:
                i = 0
                #print (sql +" is OK!")
        if ldebug :print (sql)
    if sucs and res[0]['parent'] :
        try:
            id = res[0]['parent']
            sql = 'UPDATE poi SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            print (e)
        if ldebug :print (sql)

    elif sucs and res[0]['mdd'] :
        try:
            id = res[0]['mdd']
            sql = 'UPDATE mdd SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            print (e)
        if ldebug :print (sql)

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
        print (e)
    if ldebug :print (sql)
    conn.commit()
    conn.close()

def t_poi_u_d(id,text):
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = "UPDATE poi SET text=?  WHERE id=?"
        cur.execute(sql,(text,id))
    except Exception as e:
        print (e)
    if ldebug :print (sql,text)
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
        print (e)
        cursor = ""
    if ldebug :print (sql)
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
                if ldebug : print (e)
                sucs = False
        if ldebug :print (sql)

    if sucs and res[0]['parent'] :
        try:
            id = res[0]['parent']
            sql = 'UPDATE mdd SET flag=1  WHERE id={}'.format(id)
            cur.execute(sql)
        except Exception as e:
            print (e)
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
        print (e)
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
        print (e)
    if ldebug :print (sql)
    conn.commit()
    conn.close()
