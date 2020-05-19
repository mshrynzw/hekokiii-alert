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
    count = str(cur.fetchone())
    count = count.lstrip("(")
    count = count.rstrip(",)")
    return int(count)


# SELECT文（chk_bbs.py用）
def db_check_bbs(cur, tableName):

    sql = "SELECT MAX(count) FROM {0}".format(tableName)
    cur.execute(sql)
    return cur.fetchone()


# SELECT文（chk_movie.py用）
def db_check_movie(cur, tableName, videoId):

    sql = "SELECT COUNT(*) FROM {0} WHERE  video_id = '{1}'".format(tableName, videoId)
    cur.execute(sql)
    count = str(cur.fetchone())
    count = count.lstrip("(")
    count = count.rstrip(",)")
    return int(count)


# SELECT文（chk_twitter.py用）
def db_check_twitter(cur, tableName, tweetId):

    sql = "SELECT COUNT(*) FROM {0} WHERE  id = '{1}'".format(tableName, tweetId)
    cur.execute(sql)
    count = str(cur.fetchone())
    count = count.lstrip("(")
    count = count.rstrip(",)")
    return int(count)


# INSERT文
def db_insert(cur, tableName, urlValue):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(tableName, urlValue)
    cur.execute(sql)


# INSERT文
def db_insert_bbs(cur, tableName, cnt):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(tableName, cnt)
    cur.execute(sql)


# INSERT文（chk_movie.py用）
def db_insert_movie(cur, tableName, videoId):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(tableName, videoId)
    cur.execute(sql)


# INSERT文（chk_twitter.py用）
def db_insert_tweet_id(cur, tableName, tweetId):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(tableName, tweetId)
    cur.execute(sql)


# INSERT文（chk_message_yt.py用）
def db_insert_message(cur, tableName, messages):
    sql = "INSERT INTO {0} VALUES ".format(tableName)

    for message in messages:
        data = "('{id}', '{author_external_channel_id}', '{video_id}', '{time_stamp}', {purchase_amount}), ".format(
            id=message['id'],
            author_external_channel_id=message['author_external_channel_id'],
            video_id=message['video_id'],
            time_stamp=message['time_stamp'],
            purchase_amount=['purchase_amount']
        )
        sql += data

    sql.rstrip(', ')
    cur.execute(sql)
