#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import requests
import bs4
import os
from time import sleep
from tw_reserve import tweet_reserve_live

def check_reserve_live():
    list_str = []
    community_id = os.environ["NICONICO_COMMUNITY_ID"]

    while True:

        #5分毎に予約確認を実施
        sleep(300)
        
        #HTMLスクレビング
        res = requests.get('https://com.nicovideo.jp/community/' + community_id)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elems = soup.select('.liveTitle')
        
        #<a href>のみ抽出
        for elem in elems:
            
            str_url = elem.get('href')
            #さらに放送予約URLのみ抽出
            str_url_tmp = r'http://live.nicovideo.jp/gate/lv'
            if str_url.startswith(str_url_tmp):
                
                lv_id = str_url.lstrip(str_url_tmp)
                #未ツイートの放送IDのみをツイートする。
                if not lv_id in list_str:
                    list_str.append(lv_id)
                    tweet_reserve_live(lv_id)
