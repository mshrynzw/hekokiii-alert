#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
import datetime
from time import sleep
from tw import proc_tweet

# *** 運用モード ***
# - PROD ：本番
# - TEST1：テスト（chk_comment.py以外）
# - TEST2：テスト（chk_comment.pyのみ）
MODE_SETTING = os.environ["MODE_SETTING"]
# 対象のコミュニティID
if MODE_SETTING == "PROD":
    community_id = os.environ["NICONICO_COMMUNITY_ID"]
else:
    community_id = os.environ["NICONICO_COMMUNITY_ID_TEST"]

# 曜日の設定
yobi = ["月", "火", "水", "木", "金", "土", "日"]

def set_date(date_reserve):
    date1 = date_reserve[0:10].translate(str.maketrans({"年": "/", "月": "/"}))
    date2 = datetime.datetime.strptime(date1, '%Y/%m/%d')
    date3 = date_reserve[5:10].replace("月", "/") + "(" + yobi[date2.weekday()] + ")" + date_reserve[12:17]
    return date3

def check_reserve_live():

    # ツイートのテンプレート
    strTweet = os.environ["TWEET_TPL_RESERVE"]
    listFinishedURL = []

    while True:
        try:
            sleep(20)
            #HTMLスクレビング
            res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
            # res.raise_for_status()
            soup = bs4.BeautifulSoup(res.text, "html.parser")
            elemsDate = soup.find_all("span", class_="liveDate", text=re.compile("20.*-"))
            elemsURL = soup.find_all("a", class_="liveTitle", href=re.compile(
                r"^https://live.nicovideo.jp/gate/lv"))

            listDate = []
            listURL = []
            for elemDate in elemsDate:
                listDate.append(elemDate.string)

            for elemURL in elemsURL:
                listURL.append(elemURL.get("href"))

            for i in range(len(listDate)):

                #未ツイートの放送IDのみをツイートする。
                if listURL[i] not in listFinishedURL:
                    listFinishedURL.append(listURL[i])
                    strTweet = strTweet.format("放送予約しました。", set_date(listDate[i]), listURL[i]) 
                    proc_tweet(strTweet)

                strStart =  listDate[i].translate(str.maketrans({'年':'-', '月':'-', '日':None})).replace(' -','')
                datetimeStart = datetime.datetime.strptime(strStart, '%Y-%m-%d %H:%M')
                datetimeNow = datetime.datetime.now()
                datetimeCompare = datetimeStart - datetimeNow
                secondCompare = datetimeCompare.total_seconds()

                # 1時間前にツイート
                if secondCompare > 59 * 60 and secondCompare <= 62 * 60:
                    strTweet = strTweet.format("1時間後に放送開始します。", set_date(listDate[i]), listURL[i]) 
                    proc_tweet(strTweet)
                    sleep(180)
                # 5分前にツイート
                elif secondCompare > 4 * 60 and secondCompare <= 7 * 60:
                    strTweet = strTweet.format("5分後に放送開始します。", set_date(listDate[i]), listURL[i]) 
                    proc_tweet(strTweet)
                    sleep(180)
                    
            sleep(20)
        except Exception:
            continue

        for i in range(len(listFinishedURL)):
            if listFinishedURL[i] not in listURL:
                del listFinishedURL[i]
