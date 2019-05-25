#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import bs4
import os
import re
from proc_db import db_connect, db_close, db_check_bbs, db_insert_bbs
from time import sleep
from tw import proc_tweet

# DBのテーブル名
tblName = "bbs_comment_count"
# 5chのURL
url = os.environ["5CH_URL_1"]
url_tmp = os.environ["5CH_URL_2"]
# ツイートのテンプレート
strTweet = os.environ["TWEET_TPL_BBS"]

# 掲示板を確認する
def check_bbs_count():
    try:
        headers = {'User-Agent': 'whatever'}
        res = requests.get(url_tmp, headers=headers)
        print(res.status_code)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elCntS = soup.find_all("h2", class_="is-size-7")
        elNameS = soup.find_all("span", class_="clname")
        elCmtS = soup.find_all("div", class_="clmess")

        elCntList = []
        elNameList = []
        elCmtList = []

        for elCnt in elCntS:
            elCntList.append(elCnt.text)
        for elName in elNameS:
            elNameList.append(elName.text)
        for elCmt in elCmtS:
            elCmtList.append(elCmt.text.lstrip())
    except:
        raise
    return elCntList, elNameList, elCmtList


def update_db(cntList):
    try:
        # DB接続
        arg = db_connect()
        conn = arg[0]
        cur = arg[1]
        # DB（SELECT文）
        maxCnt = db_check_bbs(cur, tblName)[0]
        if maxCnt is None:
            maxCnt = 0
        # DB切断
        db_close(conn, cur)
    except:
        raise
    return maxCnt


def tweet(cntList, nmList, cmtList, cntMxDb):
    try:
        i = 0
        for cnt in cntList:
            if int(cnt) > cntMxDb:
                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]
                # DB（INSERT文）
                db_insert_bbs(cur, tblName, int(cnt))
                # DB切断
                db_close(conn, cur)

                # Tweet
                tweet = strTweet.format(cnt, nmList[i], cmtList[i], url)
                if len(tweet) > 260:
                    cntDelStr = len(tweet) - 260
                    tweet = strTweet.format(cnt, nmList[i], cmtList[i][:-cntDelStr], url)
                proc_tweet(tweet)
            i += 1
    except:
        raise


def check_bbs():
    while True:
        try:
            countList, nameList, commentList = check_bbs_count()
            countMaxDb = update_db(countList)
            tweet(countList, nameList, commentList, countMaxDb)
        except:
            pass
        finally:
            sleep(55)
