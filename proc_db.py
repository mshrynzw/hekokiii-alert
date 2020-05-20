#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
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
        conn = psycopg2.connect(
            "host={0} port={1} dbname={2} user={3} password={4}".format(DB_HOST, DB_PORT, DB_DBNAME, DB_USER,
                                                                        DB_PASSWORD))
        conn.autocommit = True  # 自動COMMITに設定変更
        cur = conn.cursor()  # 接続開始
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
def db_insert_user(cur, table_name, user_id, user_name):
    sql = "INSERT INTO {table_name} VALUES ('{id}', '{name}')".format(
        table_name=table_name,
        id=user_id,
        name=user_name
    )
    cur.execute(sql)


# INSERT文（chk_message_yt.py用）
def db_insert_paid_chat(cur, table_name, super_chats):
    sql = "INSERT INTO {0} VALUES ".format(table_name)

    for super_chat in super_chats:
        data = "('{id}', '{author_external_channel_id}', '{video_id}', '{time_stamp}', '{video_time_stamp}', {purchase_amount}),".format(
            id=super_chat['id'],
            author_external_channel_id=super_chat['author_external_channel_id'],
            video_id=super_chat['video_id'],
            time_stamp=super_chat['time_stamp'],
            video_time_stamp=super_chat['video_time_stamp'],
            purchase_amount=super_chat['purchase_amount']
        )
        sql += data

    cur.execute(sql.rstrip(','))


# INSERT文（chk_message_yt.py用）
def db_insert_chat_text(cur, table_name, messages):
    sql = "INSERT INTO {0} VALUES ".format(table_name)

    for message in messages:
        data = "('{id}', '{author_external_channel_id}', '{video_id}', '{time_stamp}', '{video_time_stamp}', '{message}'),".format(
            id=message['id'],
            author_external_channel_id=message['author_external_channel_id'],
            video_id=message['video_id'],
            time_stamp=message['time_stamp'],
            video_time_stamp=message['video_time_stamp'],
            message=message['message']
        )
        sql += data

    cur.execute(sql.rstrip(','))


# SELECT文（chk_message_yt.py用）
def db_select_all_videos(cur, table_name):
    videos = []
    sql = "SELECT * FROM {0}".format(table_name)
    cur.execute(sql)

    for row in cur.fetchall():
        videos.append(row[0])

    return videos


# SELECT文（chk_message_yt.py用）
def db_select_user_id_list(cur, table_name):
    user_ids = []
    sql = "SELECT id FROM {0}".format(table_name)
    cur.execute(sql)

    for row in cur.fetchall():
        user_ids.append(row[0])

    return user_ids
