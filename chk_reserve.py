#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
from datetime import datetime
from time import sleep
from tw_reserve import tweet_reserve_live

def check_reserve_live():

    community_id = os.environ["NICONICO_COMMUNITY_ID"]
    listFinishedURL = []
    yobi = ["月", "火", "水", "木", "金", "土", "日"]

    while True:

        sleep(90)
        
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
            if not listURL[i] in listFinishedURL:
                listFinishedURL.append(listURL)

                date1 = listDate[i][0:10].translate(
                    str.maketrans({"年": "/", "月": "/"}))
                date2 = datetime.strptime(date1, '%Y/%m/%d')
                date3 = listDate[i][5:10].replace("月", "/") + "(" + yobi[date2.weekday()] + ")"

                strTweet = "【開始日時：" + date3 + "】" + listURL[i]
                tweet_reserve_live(strTweet)

        sleep(90)
