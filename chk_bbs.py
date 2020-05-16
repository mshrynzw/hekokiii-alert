#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from proc_db import db_connect, db_close, db_check_bbs, db_insert_bbs
from time import sleep
from tw import proc_tweet

# ログのフォーマットを定義
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(asctime)s : %(message)s')
# DBのテーブル名
tbl_name = "bbs_comment_count"
# 5chのURL
url = os.environ["5CH_URL_1"]
url_tmp = os.environ["5CH_URL_2"]
# ツイート判定用の文字数境界値
str_count_boundary_value = int(os.environ["TWEET_BBS_STR_COUNT_BOUNDARY_VALUE"])
# ツイート判定用のコメント番号の倍数
count_multiple = int(os.environ["TWEET_BBS_COUNT_MULTIPLE"])
# ツイートのテンプレート
str_tweet = os.environ["TWEET_TPL_BBS"]


# 掲示板を確認する
def check_bbs_count():
    try:
        # 【前処理】
        # オプション設定用
        options = Options()
        # GUI起動OFF（=True）
        options.headless = True
        # Chromeドライバを設定
        driver = webdriver.Chrome(chrome_options=options)

        driver.get(url_tmp)
        sleep(40)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.find_element_by_css_selector("a.d-continu").click()

        el_cnt_s = driver.find_elements_by_css_selector("h2.is-size-7")
        el_name_s = driver.find_elements_by_css_selector("span.clname")
        el_cmt_s = driver.find_elements_by_css_selector("div.clmess")

        el_cnt_list = []
        el_name_list = []
        el_cmt_list = []

        for elCnt in el_cnt_s:
            el_cnt_list.append(elCnt.text)
        for elName in el_name_s:
            el_name_list.append(elName.text)
        for elCmt in el_cmt_s:
            el_cmt_list.append(elCmt.text.lstrip())

        # 【後処理】
        driver.close()
        driver.quit()

    except Exception as e:
        logging.error(e)
        raise

    return el_cnt_list, el_name_list, el_cmt_list


def update_db():
    try:
        # DB接続
        arg = db_connect()
        conn = arg[0]
        cur = arg[1]
        # DB（SELECT文）
        max_cnt = db_check_bbs(cur, tbl_name)[0]
        if max_cnt is None:
            max_cnt = 0
        # DB切断
        db_close(conn, cur)

    except Exception as e:
        logging.error(e)
        raise

    return max_cnt


def tweet(cnt_list, nm_list, cmt_list, cnt_mx_db):
    try:
        i = 0
        for cnt in cnt_list:
            if int(cnt) > cnt_mx_db:
                # DB接続
                arg = db_connect()
                conn = arg[0]
                cur = arg[1]
                # DB（INSERT文）
                db_insert_bbs(cur, tbl_name, int(cnt))
                # DB切断
                db_close(conn, cur)

                # Tweet
                if not "http" in cmt_list[i] and (
                        len(cmt_list[i]) > str_count_boundary_value or int(cnt) % count_multiple == 0):
                    tweet = str_tweet.format(cnt, nm_list[i], cmt_list[i], url)
                    if len(tweet) > 260:
                        cnt_del_str = len(tweet) - 260
                        tweet = str_tweet.format(cnt, nm_list[i], cmt_list[i][:-cnt_del_str], url)
                    proc_tweet(tweet)
                    sleep(30)
            i += 1

    except Exception as e:
        logging.eeror(e)
        raise


def check_bbs():
    while True:
        try:
            count_list, name_list, comment_list = check_bbs_count()
            count_max_db = update_db(count_list)
            tweet(count_list, name_list, comment_list, count_max_db)

        except Exception as e:
            logging.error(e)
            pass

        finally:
            sleep(30)
