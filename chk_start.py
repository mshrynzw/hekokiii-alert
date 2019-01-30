#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
import re
from datetime import datetime
from ichiba import proc_ichiba
from time import sleep
from tw_start import tweet_start_live

def check_start_live():

    community_id = os.environ["NICONICO_COMMUNITY_ID"]
    listStartedURL = []

    while True:

        sleep(15)
        print(listStartedURL)
        #HTMLスクレビング
        res = requests.get(r"https://com.nicovideo.jp/community/" + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        try:
            elemURL = soup.find("a", class_="now_live_inner").get("href").rstrip("?ref=community")
            if elemURL not in listStartedURL:
                listStartedURL.append(elemURL)
                tweet_start_live(elemURL)
                proc_ichiba(elemURL)
        except AttributeError:
            pass

        sleep(15)
