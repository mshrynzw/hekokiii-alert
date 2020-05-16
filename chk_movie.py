#!/usr/bin/python
# -*- coding: utf-8 -*-

import bs4
import json
import os
import requests
from datetime import datetime, timedelta, timezone
from proc_db import db_connect, db_close, db_check_movie, db_insert_movie
from time import sleep
from tw import proc_tweet

# DBのテーブル名
tblName = "movie_id_list"
# ツイートのテンプレート
strTmp = os.environ["TWEET_TPL_MOVIE"]
# YouTubeのチャンネルID
channelId = os.environ["YOUTUBE_CHANNEL_ID"]
# 「YouTube Data API (v3)」のAPIキー
key = os.environ["YOUTUBE_DATA_API_KEY"]


def check_movie():


    # 動画IDを格納
    # listVideoId = []

    while True:

        # UTC（協定世界時）を取得し、「YouTube Data API (v3)」より直近1日の新規動画情報（json）を取得
        awareDT = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        req = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=" + channelId + "&key=" + key + "&publishedAfter=" + awareDT[0:23] + "Z")
        soup = bs4.BeautifulSoup(req.text, "lxml")
        jsonText = soup.p.string
        dictText = json.loads(jsonText)
        listItems = dictText.get("items")

        # 動画IDとタイトルを取得
        for listValue in listItems:

            videoId = listValue["id"]["videoId"]
            title = listValue["snippet"]["title"]

            # DB接続
            arg = db_connect()
            conn = arg[0]
            cur = arg[1]

            # DB（SELECT文）
            cnt = db_check_movie(cur, tblName, videoId)

            # DB切断
            db_close(conn, cur)

            if cnt == 0:

                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]

                # DB（INSERT文）
                db_insert_movie(cur, tblName, videoId)

                # DB切断
                db_close(conn, cur)

                strTweet = strTmp.format(title, videoId)
                proc_tweet(strTweet)

        sleep(150)
