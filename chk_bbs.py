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
url = os.environ["5CH_URL"] 
# ツイートのテンプレート
strTweet = os.environ["TWEET_TPL_BBS"]

# 掲示板を確認する
def check_bbs_count():
    try:
        res = requests.get(url + "/l10")
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elCntS = soup.find_all("span", class_="number")
        elNames = soup.find_all("span", class_="name")
        elCmtS = soup.find_all("span", class_="escaped")

        elCntList = []
        elNameList = []
        elCmtList = []

        for elCnt in elCntS:
            elCntList.append(elCnt.text)
        for elName in elNames:
            elNameList.append(elName.text)
        for elCmt in elCmtS:
            elCmtList.append(elCmt.text)
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
        maxCnt = db_check_bbs(cur, tblName)
        # DB切断
        db_close(conn, cur)
    except:
        raise
    return maxCnt


def tweet(cntList, nmList, cmtList, cntMxDb):
    try:
        i = 0
        for cnt in cntList:
            if cnt > cntMxDb:
                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]
                # DB（INSERT文）
                db_insert_bbs(cur, tblName, cnt)
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
            sleep(55)
        except:
            pass
