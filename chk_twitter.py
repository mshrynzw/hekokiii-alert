#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
import os
from proc_db import db_connect, db_close, db_check_movie, db_insert_tweet_id
from requests_oauthlib import OAuth1Session
from time import sleep
from tw import proc_tweet

# Twitter用の設定
CK = os.environ["CONSUMER_KEY"]
CS = os.environ["CONSUMER_SECRET"]
AT = os.environ["ACCESS_TOKEN"]
ATS = os.environ["ACCESS_TOKEN_SECRET"]

# Twitter検索の設定
keyword = os.environ["TWEET_SEARCH_KEYWORD"]
from_user = os.environ["TWEET_SEARCH_FROM_USER"]

# DBのテーブル名
tblName = "tweet_id_list"
# ツイートのテンプレート
strTmp = os.environ["TWEET_TPL_INFO"]


def check_twitter():

    while True:
        # 本日の日付を取得
        today = datetime.date.today().strftime('%Y-%m-%d')
        
        # ツイートポストエンドポイント
        url = "https://api.twitter.com/1.1/search/tweets.json"
        query = keyword + " from:" + from_user + " since:" + today
        params = {'q' : query, 'count' : 10}
        # 認証処理
        twitter = OAuth1Session(CK, CS, AT, ATS)
        # post送信
        res = twitter.get(url, params=params)

        if res.status_code == 200:  # 正常投稿出来た場合

            results = json.loads(res.text)

            for tweet in results['statuses']:

                tweetId = tweet['id']
                strTweet = strTmp.format(text=tweet['text'])

                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]
                #S ELECT処理
                cnt = db_check_movie(cur, tblName, tweetId)
                # DB切断
                db_close(conn, cur)

                if cnt == 0:
                    # DB接続
                    arg = db_connect()
                    conn = arg[0]
                    cur = arg[1]

                    # DB（INSERT文）
                    db_insert_tweet_id(cur, tblName, tweetId)

                    # DB切断
                    db_close(conn, cur)

                    #ツイート
                    proc_tweet(strTweet)
                
        sleep(150)
