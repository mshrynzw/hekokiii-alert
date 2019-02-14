#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import os
import psycopg2

# DB接続情報
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
DB_DBNAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

# DB接続
def db_connect():

    try:
        conn = psycopg2.connect("host={0} port={1} dbname={2} user={3} password={4}".format(DB_HOST, DB_PORT, DB_DBNAME, DB_USER, DB_PASSWORD))
        conn.autocommit = True  # 自動COMMITに設定変更
        cur = conn.cursor()     # 接続開始
        return conn, cur
    except Exception as e:
        raise Exception(e)

# DB切断
def db_close(conn, cur):

    try:
        cur.close()
        conn.close()
    except Exception as e:
        raise Exception(e)

# SELECT文
def db_check(cur, tableName, urlValue):

    sql = "SELECT COUNT(*) FROM {0} WHERE  url = '{1}'".format(tableName, urlValue)
    cur.execute(sql)
    return cur.fetchone()

# INSERT文
def db_insert(cur, tableName, urlValue):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(tableName, urlValue)
    cur.execute(sql)
    