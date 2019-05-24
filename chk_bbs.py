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
        print("★001")
        #res.raise_for_status()
        print("★002")
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        print("★003")
        elCntS = soup.find_all("span", class_="number")
        print("★004")
        elNames = soup.find_all("span", class_="name")
        print("★005")
        elCmtS = soup.find_all("span", class_="escaped")
        print("★00")

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
        print("★01")
        raise
    return elCntList, elNameList, elCmtList


def update_db(cntList):
    try:
        # DB接続
        arg = db_connect()
        conn = arg[0]
        cur = arg[1]
        print("★02")
        # DB（SELECT文）
        maxCnt = db_check_bbs(cur, tblName)
        print("★03")
        # DB切断
        db_close(conn, cur)
        print("★04")
    except:
        print("★05")
        raise
    return maxCnt


def tweet(cntList, nmList, cmtList, cntMxDb):
    try:
        i = 0
        for cnt in cntList:
            if cnt > cntMxDb:
                print("★06")
                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]
                print("★07")
                # DB（INSERT文）
                db_insert_bbs(cur, tblName, cnt)
                print("★08")
                # DB切断
                db_close(conn, cur)
                print("★09")

                # Tweet
                tweet = strTweet.format(cnt, nmList[i], cmtList[i], url)
                print("★10")
                if len(tweet) > 260:
                    print("★11")
                    cntDelStr = len(tweet) - 260
                    print("★12")
                    tweet = strTweet.format(cnt, nmList[i], cmtList[i][:-cntDelStr], url)
                    print("★13")
                proc_tweet(tweet)
                print("★14")

            i += 1
            print("★15")
    except:
        print("★16")
        raise


def check_bbs():
    while True:
        try:
            countList, nameList, commentList = check_bbs_count()
            countMaxDb = update_db(countList)
            tweet(countList, nameList, commentList, countMaxDb)
        except:
            print("★17")
            pass
        finally:
            sleep(55)
