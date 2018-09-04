#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
from time import sleep
from alert_tweet_reserve import alert_tweet_reserve

list_str = []

while True:
    sleep(300)
    res = requests.get('https://com.nicovideo.jp/community/co2388471')
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    elems = soup.select('.liveTitle')
    for elem in elems:
        str_url = elem.get('href')
        str_url_tmp = r'http://live.nicovideo.jp/gate/lv'
        if str_url.startswith(str_url_tmp):
            lv_id = str_url.lstrip(str_url_tmp)
            if not lv_id in list_str:
                list_str.append(lv_id)
                alert_tweet_reserve(lv_id)
