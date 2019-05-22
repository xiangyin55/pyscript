# -*- encoding: utf-8 -*-

import sqlite3
import json
import mod.logger as logger
import time

class database:

    log = logger.logger("debug",log_name=time.strftime("db-%Y-%m-%d.log", time.localtime()))

    def __init__(self, dbpath):
        self.dbpath = dbpath if dbpath else "dat\\meet.db"

        self.t_c()

    def _opendb(self):
        conn = sqlite3.connect(self.dbpath)
        cur = conn.cursor()
        return conn,cur

    def _closedb(self,conn):
        conn.commit()
        conn.close()



    def _isql(self,t,o):
        sql = ''
        k,v = '',''
        for item in o:
            try:
                if isinstance(o[item],int) or isinstance(o[item],float) :
                    s = str(o[item])
                else:
                    s = '"'+o[item]+'"'
                k += item if not k else ','+item
                v += s if not v else ','+s
            except Exception as e:
                self.log.warning(o)
                self.log.warning(e)

        sql = 'INSERT INTO {} ({}) VALUES ( {} )'.format(t,k,v)

        #self.log.debug(sql)

        return sql

    def _usql(self,t,o):
        sql = ''
        s = ''
        for item in o:
            if item =='id': continue
            s += ',' if s else ''
            if isinstance(o[item],int) or isinstance(o[item],float) :
                s += "{}={}".format(item,str(o[item]))
            else:
                s += '{}="{}"'.format(item,o[item].replace('"',''))

        sql = 'UPDATE {} SET {} WHERE id="{}"'.format(t,s,o['id'])

        return sql


    def t_c (self):
        conn,cur = self._opendb()


        create_table_district ='''
        create table IF NOT EXISTS district (
            id      TEXT NOT NULL PRIMARY KEY,
            name    TEXT,
            area    TEXT,
            count   INTEGER default 0,
            flag    INTEGER  default 0
        );
        '''
        cur.executescript(create_table_district)

        create_table_category ='''
        create table IF NOT EXISTS category (
            id      TEXT PRIMARY KEY ,
            classify    TEXT,
            name    TEXT
        );
        '''
        cur.executescript(create_table_category)

        create_table_pois = '''
        CREATE TABLE  IF NOT EXISTS pois (
            id     TEXT NOT NULL PRIMARY KEY,
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

        create_table_shape ='''
        create table IF NOT EXISTS shape (
            id      TEXT PRIMARY KEY ,
            shape   TEXT
        );
        '''
        cur.executescript(create_table_shape)

        create_table_scenic ='''
        create table IF NOT EXISTS scenic (
            id       text not null PRIMARY KEY ,
            poi      text not null,
            classify text not null,
            parent   text,
            text     text,
            url      text
        );
        '''
        cur.executescript(create_table_scenic)

        create_table_image ='''
        create table IF NOT EXISTS image (
            id      text not null  PRIMARY KEY,
            poi       text not null,
            parent   text,
            flag     INTEGER  default 0
        );
        --CREATE UNIQUE INDEX if not exists  image_i ON intro(id, url);
        '''
        cur.executescript(create_table_image)

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

        self._closedb(conn)
        return


    def t_s (self,k):

        jsql = {

            'province': 'SELECT id  from district where area is null',
            'image': 'SELECT id  from image where flag=0',
            'pickimage': 'SELECT id  from image where flag=1',
            'level': "SELECT id,name,x,y,adcode,star,show from pois where type='aoi' and star like 'A%' order by star desc, zoom, score desc,tag"
            }

        if not k in jsql:
            log.error('{} is not in select sql list!'.format(s))
            return -1

        conn,cur = self._opendb()
        self.log.debug (jsql[k])

        try:
            cursor  = cur.execute(jsql[k]).fetchall()
        except Exception as e:
            self.log.warning(e)
            cursor = ""


        self._closedb(conn)
        return cursor


    def t_s_byid (self,k,id):

        jsql = {
            'city': 'SELECT name,id  from district where id="{}"'.format(id)  #查询城市名称
            }

        if not k in jsql:
            log.error('{} is not in select sql list!'.format(s))
            return -1

        conn,cur = self._opendb()
        self.log.debug (jsql[k])

        try:
            cursor  = cur.execute(jsql[k]).fetchall()
        except Exception as e:
            self.log.warning(e)
            cursor = ""


        self._closedb(conn)
        return cursor


    def t_u(self,t,o):
        conn,cur = self._opendb()
        sucs = True
        sql = self._usql(t,o)
        try:
            cur.execute(sql)
        except Exception as e:
            self.log.warning(sql)
            self.log.warning(e)
            sucs = False

        self._closedb(conn)
        return sucs

    def t_a (self,t,o,force=False,fcontinue=False):
        # force :数据insert识别后是否尝试 update
        if not t or not o :
            self.log.error('table or content is null!')
            return -1

        conn,cur = self._opendb()
        sucs = True
        for r in o:
            # 尝试插入数据
            sql = self._isql(t,r)

            try:
                cur.execute(sql)
                continue
            except Exception as e:
                sucs = False
                if not force:
                    self.log.warning(sql)
                    self.log.warning(e)


            if not sucs and not force :
                if fcontinue: continue
                else: break

            sql = self._usql(t,r)
            try:

                cur.execute(sql)
                sucs = True
            except Exception as e:
                self.log.warning(sql)
                self.log.warning(e)
                sucs = False

            if not sucs and not fcontinue: break

        self._closedb(conn)
        return sucs


if __name__ == '__main__':

    d = database('..\\dat\\meet.db')
    s = d.t_s('mdd')
    print (s)




