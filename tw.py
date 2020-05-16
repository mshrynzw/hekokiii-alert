#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from distutils.util import strtobool
from requests_oauthlib import OAuth1Session

# *** 運用モード ***
# - PROD ：本番
# - TEST1：テスト（chk_comment.py以外）
# - TEST2：テスト（chk_comment.pyのみ）
MODE_SETTING = os.environ["MODE_SETTING"]

# Twitter用の設定
CK = os.environ["CONSUMER_KEY"]
CS = os.environ["CONSUMER_SECRET"]
AT = os.environ["ACCESS_TOKEN"]
ATS = os.environ["ACCESS_TOKEN_SECRET"]
# ログのフォーマットを定義
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(asctime)s : %(message)s')


def proc_tweet(strTweet):

    if MODE_SETTING == "PROD":
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
            logging.warning("[ERR] Tweet : " + strTweet + "(" + str(res.status_code) + ")")
    else:
        logging.info("[OK] TEST : " + strTweet )
