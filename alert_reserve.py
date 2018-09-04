#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
from time import sleep
from alert_tweet_reserve import alert_tweet_reserve

res = requests.get('https://com.nicovideo.jp/community/co2388471')
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, "html.parser")
elems = soup.select('.liveTitle')
for elem in elems:
    str_url = elem.get('href')
    str_url_tmp = r'http://live.nicovideo.jp/gate/lv'
    if str_url.startswith(str_url_tmp):
        alert_tweet_reserve(str_url.lstrip(str_url_tmp))
