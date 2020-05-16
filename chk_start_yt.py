#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import bs4
import json
import os
import requests
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from proc_db import db_connect, db_close, db_check_movie, db_insert_movie
from time import sleep
from tw import proc_tweet

# DBのテーブル名
tblName = "start_youtube_video_id_list"
# ツイートのテンプレート
strTmp = os.environ["TWEET_TPL_START_YOUTUBE"]
# YouTubeのチャンネルID
channelId = os.environ["YOUTUBE_CHANNEL_ID_HEKOKI"]
# 「YouTube Data API (v3)」のAPIキー
key = os.environ["YOUTUBE_DATA_API_KEY"]

def check_start_yt():

    while True:

        # 【前処理】
        # オプション設定用
        options = Options()
        # GUI起動OFF（=True）
        options.set_headless(True)
        # Chromeドライバを設定
        driver = webdriver.Chrome(chrome_options=options)

        try:
            driver.get(r"https://www.youtube.com/channel/{channelId}".format(channelId=channelId))
            if driver.find_element_by_xpath(r'//*[@id="badges"]/div/span') == "ライブ配信中":

                videoId = driver.find_element_by_xpath(r'//*[@id="video-title"]').get_attribute('href').replace(r'/', '')
                url = r"https://www.youtube.com/" + videoId

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

                    strTweet = strTmp.format(url=url)
                    proc_tweet(strTweet)

        except Exception as e:
            logging.error(e)

        finally:
            driver.quit()

        sleep(60)
