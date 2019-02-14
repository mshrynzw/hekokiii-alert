#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import bs4
import os
import re
import requests
import threading
from datetime import datetime
from ichiba import proc_ichiba
from time import sleep
from tw import proc_tweet

# テスト用フラグ（Trueの場合は、ツイートせずログのみ出力する。）
FT = os.environ["FLG_TEST"]
# 対象のコミュニティID
if FT:
    community_id = os.environ["NICONICO_COMMUNITY_ID_TEST"]
else:
    community_id = os.environ["NICONICO_COMMUNITY_ID"]

# ツイートのテンプレート
strTweet = os.environ["TWEET_TPL_START"]

def check_start_live():

    listStartedURL = []

    while True:

        sleep(15)
        #HTMLスクレビング
        res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        try:
            elemURL = soup.find("a", class_="now_live_inner").get("href").rstrip("?ref=community")
            if elemURL not in listStartedURL:
                listStartedURL.append(elemURL)
                proc_tweet(strTweet + elemURL)
                threadChkStart_1 = threading.Thread(target=proc_ichiba, args=(elemURL,))
                threadChkStart_1.start()
                print("ご注文はうさぎですか？")
        except AttributeError:
            pass
        print("ご注文はうさぎですか？？")

        sleep(15)
