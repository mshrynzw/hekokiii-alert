#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from proc_db import db_connect, db_close, db_check_movie, db_insert_movie
from time import sleep
from tw import proc_tweet

# ツイートのテンプレート
str_tmp = os.environ["TWEET_TPL_START_YOUTUBE"]
# YouTubeのチャンネルIDÒ
channel_id = os.environ["YOUTUBE_CHANNEL_ID_HEKOKI"]
# 「YouTube Data API (v3)」のAPIキー
key = os.environ["YOUTUBE_DATA_API_KEY"]


def check_start_yt():
    while True:

        # 【前処理】
        # オプション設定用
        options = Options()
        # GUI起動OFF（=True）
        options.headless = True
        # Chromeドライバを設定
        driver = webdriver.Chrome(chrome_options=options)
        driver.implicitly_wait(10)

        try:
            driver.get(r"https://www.youtube.com/channel/{channel_id}".format(channel_id=channel_id))

            if driver.find_element_by_xpath(r'//*[@id="badges"]/div/span').text == "LIVE NOW":

                url = driver.find_element_by_xpath(r'//*[@id="video-title"]').get_attribute('href')
                video_id = url.replace(r'https://www.youtube.com/watch?v=', '')

                # DB（SELECT文）
                cnt = db_check_movie(video_id)

                if cnt == 0:
                    # DB（INSERT文）
                    db_insert_movie(video_id)

                    # ツイート
                    str_tweet = str_tmp.format(url=url)
                    proc_tweet(str_tweet)

        except NoSuchElementException as e:
            logging.info("Not currently broadcasting YouTube Live.")

        except Exception as e:
            logging.error(e)

        finally:
            driver.quit()

        sleep(50)
