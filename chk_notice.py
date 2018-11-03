#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
from datetime import datetime, timedelta
from time import sleep
from tw_notice import tweet_notice

def check_notice():

    community_id = os.environ["NICONICO_COMMUNITY_ID"]
    listFinishedNoticeTitle = []
    listFinishedNoticeText = []
    yobi = ["月", "火", "水", "木", "金", "土", "日"]

    while True:

        sleep(30)
        
        # HTMLスクレビング
        res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elemsNoticeTitle = soup.find_all("h3", class_="noticeTitle")
        elemsNoticeDate = soup.find_all("span", class_="date")
        elemsNoticeText = soup.find_all("p", class_="notice_text")

        listNoticeTitle = []
        listNoticeDate = []
        listNoticeText = []

        for elemNoticeTitle in elemsNoticeTitle:
            listNoticeTitle.append(elemNoticeTitle.string)
        for elemNoticeDate in elemsNoticeDate:
            listNoticeDate.append(elemNoticeDate.string)
        for elemNoticeText in elemsNoticeText:
            listNoticeText.append(elemNoticeText.string)

        for i in range(len(listNoticeDate)):
            # 未ツイートのお知らせのみをツイートする。
            if listNoticeText[i] not in listFinishedNoticeText:

                date1 = listNoticeDate[i][0:10].translate(str.maketrans({"年": "/", "月": "/"}))
                datetime1 = datetime(int(listNoticeDate[i][0:4]), int(listNoticeDate[i][5:7]), int(listNoticeDate[i][8:10]))

                # お知らせ日時が1日以内のみをツイートする。
                if datetime1 + timedelta(days=1) > datetime.now():

                    listFinishedNoticeTitle.append(listNoticeTitle[i])
                    listFinishedNoticeText.append(listNoticeText[i])

                    date2 = datetime.strptime(date1, '%Y/%m/%d')
                    date3 = listNoticeDate[i][5:10].replace(
                        "月", "/") + "(" + yobi[date2.weekday()] + ")" + listNoticeDate[i][12:17]

                    strTweet =  "【通知】 #世界の屁こき隊 がお知らせしました。【通知日時：" + date3 + "】\n" + \
                                "[タイトル]" + "\n" + \
                                listNoticeTitle[i] + "\n" + \
                                "[本文]" + "\n" + \
                                listNoticeText[i] + "\n" + \
                                r"https://com.nicovideo.jp/community/" + community_id
                    tweet_notice(strTweet)

        sleep(30)

        for i in range(len(listFinishedNoticeText)):
            if listFinishedNoticeText[i] not in listNoticeText:
                del listFinishedNoticeText[i]
