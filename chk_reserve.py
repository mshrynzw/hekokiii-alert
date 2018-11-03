#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
import datetime
from time import sleep
from tw_reserve import tweet_reserve_live

def check_reserve_live():

    community_id = os.environ["NICONICO_COMMUNITY_ID"]
    listFinishedURL = []
    yobi = ["月", "火", "水", "木", "金", "土", "日"]

    while True:

        sleep(30)
        print(listFinishedURL)
        #HTMLスクレビング
        res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elemsDate = soup.find_all("span", class_="liveDate", text=re.compile("20.*-"))
        elemsURL = soup.find_all("a", class_="liveTitle", href=re.compile(
            r"^http://live.nicovideo.jp/gate/lv"))

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
                date1 = listDate[i][0:10].translate(
                    str.maketrans({"年": "/", "月": "/"}))
                date2 = datetime.datetime.strptime(date1, '%Y/%m/%d')
                date3 = listDate[i][5:10].replace(
                    "月", "/") + "(" + yobi[date2.weekday()] + ")" + listDate[i][12:17]
                strTweet = "【予約】 #世界の屁こき隊 が放送予約しました。【開始日時：" + date3 + "】" + listURL[i]
                tweet_reserve_live(strTweet)

            strStart =  listDate[i].translate(str.maketrans({'年':'-', '月':'-', '日':None})).replace(' -','')
            datetimeStart = datetime.datetime.strptime(strStart, '%Y-%m-%d %H:%M')
            datetimeNow = datetime.datetime.now()
            datetimeCompare = datetimeStart - datetimeNow
            secondCompare = datetimeCompare.seconds
            # 1時間前にツイート
            if secondCompare > 59 * 60 and secondCompare <= 60 * 60:
                date1 = listDate[i][0:10].translate(
                    str.maketrans({"年": "/", "月": "/"}))
                date2 = datetime.datetime.strptime(date1, '%Y/%m/%d')
                date3 = listDate[i][5:10].replace(
                    "月", "/") + "(" + yobi[date2.weekday()] + ")" + listDate[i][12:17]
                strTweet = "【予約】 #世界の屁こき隊 が1時間後に放送開始します。【開始日時：" + date3 + "】" + listURL[i]
                tweet_reserve_live(strTweet)
            # 5分前にツイート
            elif secondCompare > 4 * 60 and secondCompare <= 5 * 60:
                date1 = listDate[i][0:10].translate(
                    str.maketrans({"年": "/", "月": "/"}))
                date2 = datetime.datetime.strptime(date1, '%Y/%m/%d')
                date3 = listDate[i][5:10].replace(
                    "月", "/") + "(" + yobi[date2.weekday()] + ")" + listDate[i][12:17]
                strTweet = "【予約】 #世界の屁こき隊 が5分後に放送開始します。【開始日時：" + date3 + "】" + listURL[i]
                tweet_reserve_live(strTweet)

        sleep(30)

        for i in range(len(listFinishedURL)):
            if listFinishedURL[i] not in listURL:
                del listFinishedURL[i]
