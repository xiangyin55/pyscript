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

if 'dbpath' not in locals().keys() : dbpath = u'db\\bany.db'
if 'ldebug' not in locals().keys() : ldebug = True

def t_c ():
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    create_table_city ='''
    create table IF NOT EXISTS city (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        level   INTEGER,
        name    TEXT,
        text    TEXT,
        flag INTEGER  default 0

    );
    '''
    cur.executescript(create_table_city)

    create_table_scenic ='''
    create table IF NOT EXISTS scenic (
        id      TEXT NOT NULL PRIMARY KEY,
        parent  TEXT,
        city    TEXT,
        level   INTEGER,
        name    TEXT,
        text    TEXT,
        aoi     INTEGER  default 0,
        poi     INTEGER  default 0
    );
    '''
    cur.executescript(create_table_ids)

    conn.commit()
    conn.close()
    return

def t_a (res,):
    if not res : return
    flag = ['','provice','city','aoi','poi']
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    sucs = True
    for r in res:
        try:
            sql = 'INSERT INTO ids (id,parent,level,name) VALUES ( "{}","{}",{},"{}" )'.format(r['id'],r['parent'],r['level'],r['name'])
            cur.execute(sql)
        except Exception as e:
            try:
                sql = 'UPDATE ids SET parent="{}", level={}, name="{}" WHERE id="{}"'.format(r['parent'],r['level'],r['name'],r['id'])
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
            field = flag[ res[0]['level']-1]
            sql = 'UPDATE ids SET {0}=1  WHERE id={1}'.format(field,id)
            cur.execute(sql)
        except Exception as e:
            print (e)
        if ldebug :print (sql)

    conn.commit()
    conn.close()
    return

    return

def t_ids_u(id,level):
    flag = ['','provice','city','aoi','poi']
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'UPDATE ids SET {0}=2  WHERE id="{1}"'.format(flag[level],id)
        cur.execute(sql)
    except Exception as e:
        print (e)
    if ldebug :print (sql)
    conn.commit()
    conn.close()

def t_ids_s (level=2):
    flag = ['','provice','city','aoi','poi']
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()
    try:
        sql = 'SELECT id  from ids where level={0} and {1}=0'.format(level,flag[level])
        cursor  = cur.execute(sql).fetchall()
    except Exception as e:
        print (e)
        cursor = ""
    if ldebug :print (sql)
    conn.commit()
    conn.close()
    return cursor