#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
from time import sleep
from tw_reserve import tweet_reserve_live

def check_reserve_live():

    community_id = os.environ["NICONICO_COMMUNITY_ID"]
    listFinishedURL = []

    while True:

        #3分毎に予約確認を実施
        sleep(180)
        
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
                strTweet = "（開始日時：" + listDate[i][:-1].replace(" ","") + "）" + listURL[i]
                tweet_reserve_live(strTweet)
