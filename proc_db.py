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


def get_connection():
    try:
        return psycopg2.connect(
            "host={0} port={1} dbname={2} user={3} password={4}".format(DB_HOST, DB_PORT, DB_DBNAME, DB_USER,
                                                                        DB_PASSWORD))
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
def db_check(cur, table_name, url_value):
    sql = "SELECT COUNT(*) FROM {0} WHERE  url = '{1}'".format(table_name, url_value)
    cur.execute(sql)
    count = str(cur.fetchone())
    count = count.lstrip("(")
    count = count.rstrip(",)")
    return int(count)


# SELECT文（chk_bbs.py用）
def db_check_bbs(cur, table_name):
    sql = "SELECT MAX(count) FROM {0}".format(table_name)
    cur.execute(sql)
    return cur.fetchone()


# SELECT文（chk_movie.py用）
def db_check_movie(video_id):
    stmt = "SELECT COUNT(id) FROM youtube_video WHERE id = '{video_id}'".format(
        video_id=video_id
    )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt)
            count = cur.fetchone()

    return count[0]


# SELECT文（chk_twitter.py用）
def db_check_twitter(cur, table_name, tweet_id):
    sql = "SELECT COUNT(*) FROM {0} WHERE  id = '{1}'".format(table_name, tweet_id)
    cur.execute(sql)
    count = str(cur.fetchone())
    count = count.lstrip("(")
    count = count.rstrip(",)")
    return int(count)


# INSERT文
def db_insert(cur, table_name, url_value):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(table_name, url_value)
    cur.execute(sql)


# INSERT文
def db_insert_bbs(cur, table_name, cnt):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(table_name, cnt)
    cur.execute(sql)


# INSERT文（chk_movie.py用）
def db_insert_movie(video_id):
    stmt = "INSERT INTO youtube_video (id, has_got_messages) VALUES (%s, false)"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt, (
                video_id,
            ))
            conn.commit()


# INSERT文（chk_twitter.py用）
def db_insert_tweet_id(cur, table_name, tweet_id):
    sql = "INSERT INTO {0} VALUES ('{1}')".format(table_name, tweet_id)
    cur.execute(sql)


# UPDATE文（chk_message_yt.py用）
def db_update_video_has_got_messages(video_id):
    stmt = "UPDATE youtube_video SET has_got_messages = TRUE WHERE id = '{video_id}';"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt.format(
                video_id=video_id
            ))
            conn.commit()


# INSERT文（chk_message_yt.py用）
def db_insert_user(user_id, user_name):
    stmt = "INSERT INTO youtube_user VALUES (%s, %s) ON CONFLICT DO NOTHING;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt, (
                user_id,
                user_name
            ))
            conn.commit()


# INSERT文（chk_message_yt.py用）
def db_insert_paid_chat(super_chats):
    stmt = "INSERT INTO youtube_super_chat VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            for super_chat in super_chats:
                cur.execute(stmt, (
                    super_chat['id'],
                    super_chat['author_external_channel_id'],
                    super_chat['video_id'],
                    super_chat['time_stamp'],
                    super_chat['video_time_stamp'],
                    super_chat['purchase_amount']
                ))
            conn.commit()


# INSERT文（chk_message_yt.py用）
def db_insert_chat_text(messages):
    stmt = "INSERT INTO youtube_message VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;"

    with get_connection() as conn:
        with conn.cursor() as cur:
            for message in messages:
                cur.execute(stmt, (
                    message['id'],
                    message['author_external_channel_id'],
                    message['video_id'],
                    message['time_stamp'],
                    message['video_time_stamp'],
                    message['message']
                ))
            conn.commit()


# SELECT文（chk_message_yt.py用）
def db_select_all_videos():
    videos = []
    stmt = "SELECT id FROM youtube_video WHERE has_got_messages = FALSE"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt)
            conn.commit()

            for row in cur.fetchall():
                videos.append(row[0])

    return videos


# SELECT文（chk_message_yt.py用）
def db_select_user_id_list():
    user_ids = []
    stmt = "SELECT id FROM youtube_user"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(stmt)
            conn.commit()

            for row in cur.fetchall():
                user_ids.append(row[0])

    return user_ids
