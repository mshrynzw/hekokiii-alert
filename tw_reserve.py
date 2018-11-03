#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from requests_oauthlib import OAuth1Session

# Twitter用の設定
CK = os.environ["CONSUMER_KEY"]
CS = os.environ["CONSUMER_SECRET"]
AT = os.environ["ACCESS_TOKEN"]
ATS = os.environ["ACCESS_TOKEN_SECRET"]

def tweet_reserve_live(tweet):

    # 認証処理
    twitter = OAuth1Session(CK, CS, AT, ATS)
    # ツイートポストエンドポイント
    url = "https://api.twitter.com/1.1/statuses/update.json"
    # post送信
    print(tweet)
    params = {"status": tweet}
    res = twitter.post(url, params=params)

    if res.status_code == 200:  # 正常投稿出来た場合
        print("【ツイート完了】")
    else:                       # 正常投稿出来なかった場合
        print("【ツイート失敗】 : %d" % res.status_code)
