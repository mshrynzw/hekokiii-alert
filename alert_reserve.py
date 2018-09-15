#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import bs4
import copy
import os
import requests
from time import sleep
from tw_reserve import tweet_reserve_live

def check_reserve_live():

    list_before = []    # 更新前の放送ID一覧
    list_after = []     # 更新後の放送ID一覧
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
                if not lv_id in list_after:
                    list_after.append(lv_id)
                    tweet_reserve_live(lv_id)
                
        list_diff = set(list_before) - set(list_after)
        for elem in list_diff:
            list_after.remove(elem)
        list_before = copy.deepcopy(list_after)
