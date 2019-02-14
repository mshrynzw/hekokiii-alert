#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from requests_oauthlib import OAuth1Session

# テスト用フラグ（Trueの場合は、ツイートせずログのみ出力する。）
FT = os.environ["FLG_TEST"]
# Twitter用の設定
CK = os.environ["CONSUMER_KEY"]
CS = os.environ["CONSUMER_SECRET"]
AT = os.environ["ACCESS_TOKEN"]
ATS = os.environ["ACCESS_TOKEN_SECRET"]

# ログのフォーマットを定義
logging.basicConfig(level=logging.INFO, format=os.environ["LOG_FORMAT"])

def proc_tweet(strTweet):

    if FT:
        logging.info("[OK][TEST] : " + strTweet )
    else:
        # 認証処理
        twitter = OAuth1Session(CK, CS, AT, ATS)
        # ツイートポストエンドポイント
        url = "https://api.twitter.com/1.1/statuses/update.json"
        # post送信
        params = {"status": strTweet}
        res = twitter.post(url, params=params)

        if res.status_code == 200:  # 正常投稿出来た場合
            logging.info("[OK] Tweet : " + strTweet )
        else:                       # 正常投稿出来なかった場合
            logging.warning("[ERR]Tweet : " + strTweet + "(" + res.status_code + ")")
