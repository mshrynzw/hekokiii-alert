#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
from requests_oauthlib import OAuth1Session

# Twitter用の設定
CK = os.environ["CONSUMER_KEY"]
CS = os.environ["CONSUMER_SECRET"]
AT = os.environ["ACCESS_TOKEN"]
ATS = os.environ["ACCESS_TOKEN_SECRET"]

# ツイートのテンプレート
tweet_tpl = os.environ["TWEET_CMT"]

def tweet_comment(bloadcast_id):

    # 認証処理
    twitter = OAuth1Session(CK, CS, AT, ATS)
    # ツイートポストエンドポイント
    url_media = "https://upload.twitter.com/1.1/media/upload.json"
    url = "https://api.twitter.com/1.1/statuses/update.json"

    # 画像投稿
    files = {"media": open('./tmp/figure.jpg', 'rb')}
    req_media = twitter.post(url_media, files=files)

    # レスポンスを確認
    if req_media.status_code != 200:
        print("画像アップデート失敗: %s", req_media.text)
        exit()

    # Media ID を取得
    media_id = json.loads(req_media.text)['media_id']
    print("Media ID: %d" % media_id)

    # post送信
    tweet = tweet_tpl + bloadcast_id
    print(tweet)
    params = {"status": tweet, "media_ids": [media_id]}
    res = twitter.post(url, params=params)

    if res.status_code == 200:  # 正常投稿出来た場合
        print("【ツイート完了】")
    else:                       # 正常投稿出来なかった場合
        print("【ツイート失敗】 : %d" % res.status_code)
