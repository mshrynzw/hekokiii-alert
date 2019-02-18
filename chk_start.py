#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import bs4
import os
import re
import requests
import threading
from datetime import datetime
from ichiba import proc_ichiba
from chk_comment import check_comment
from proc_db import db_connect, db_close,db_check, db_insert
from time import sleep
from tw import proc_tweet

# *** 運用モード ***
# - PROD ：本番
# - TEST1：テスト（chk_comment.py以外）
# - TEST2：テスト（chk_comment.pyのみ）
MODE_SETTING = os.environ["MODE_SETTING"]
# 対象のコミュニティID
if MODE_SETTING == "PROD":
    community_id = os.environ["NICONICO_COMMUNITY_ID"]
else:
    community_id = os.environ["NICONICO_COMMUNITY_ID_TEST"]

# DBのテーブル名
dbName = "list_started_url"
# ツイートのテンプレート
strTweet = os.environ["TWEET_TPL_START"]


def check_start_live():
    while True:

        sleep(15)
        #HTMLスクレビング
        res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        try:
            bloadcast_url = soup.find("a", class_="now_live_inner").get("href").rstrip("?ref=community")

            # DB接続
            arg = db_connect()
            conn = arg[0]
            cur = arg[1]
            
            # DB（SELECT文）
            count = db_check(cur, dbName, bloadcast_url)

            if count == 0:
                db_insert(cur, dbName, bloadcast_url)
                proc_tweet(strTweet + bloadcast_url)
                threadChkStart_1 = threading.Thread(target=proc_ichiba, args=(bloadcast_url,))
                threadChkStart_2 = threading.Thread(target=check_comment, args=(bloadcast_url,))
                threadChkStart_1.start()
                threadChkStart_2.start()
            db_close(conn, cur)

        except AttributeError:
            pass

        sleep(15)
