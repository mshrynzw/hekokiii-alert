#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import bs4
import os
import re
import requests
import threading
from datetime import datetime
from ichiba import proc_ichiba
from proc_db import db_connect, db_close,db_check, db_insert
from time import sleep
from tw import proc_tweet

# テスト用フラグ（Trueの場合は、ツイートせずログのみ出力する。）
FT = os.environ["FLG_TEST"]
# 対象のコミュニティID
if FT:
    community_id = os.environ["NICONICO_COMMUNITY_ID_TEST"]
else:
    community_id = os.environ["NICONICO_COMMUNITY_ID"]
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
            elemURL = soup.find("a", class_="now_live_inner").get("href").rstrip("?ref=community")

            # DB接続
            arg = db_connect()
            conn = arg[0]
            cur = arg[1]
            
            # DB（SELECT文）
            count = db_check(cur, dbName, elemURL)
            print(count)

            if count == 0:
                db_insert(cur, dbName, elemURL)
                proc_tweet(strTweet + elemURL)
                threadChkStart_1 = threading.Thread(target=proc_ichiba, args=(elemURL,))
                threadChkStart_1.start()
            db_close(conn, cur)

        except AttributeError:
            pass

        sleep(15)
