#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import json
import os
from requests_oauthlib import OAuth1Session

# *** 運用モード（本モジュール内では未使用） ***
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


def tweet_comment(strTweet):
    # 認証処理
    twitter = OAuth1Session(CK, CS, AT, ATS)
    # ツイートポストエンドポイント
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    url = "https://api.twitter.com/1.1/statuses/update.json"

    # 画像投稿
    files = {"media": open('./tmp/figure.png', 'rb')}
    req_media = twitter.post(url_media, files=files)

    # レスポンスを確認
    if req_media.status_code != 200:
        logging.warning("画像アップデート失敗: %s", req_media.text)
        exit()

    # Media ID を取得
    media_id = json.loads(req_media.text)['media_id']
    logging.info("Media ID: %d" % media_id)

    # post送信
    logging.info(strTweet)
    params = {"status": strTweet, "media_ids": [media_id]}
    res = twitter.post(url, params=params)

    if res.status_code == 200:  # 正常投稿出来た場合
        logging.info("【ツイート完了】")
    else:                       # 正常投稿出来なかった場合
        logging.warning("【ツイート失敗】 : %d" % res.status_code)
