#encoding:utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.options import Options
from time import sleep
import logging
import os

# ログのフォーマットを定義
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(asctime)s : %(message)s')
# 特定の商品のセット
listItems = ["azB01HR3DR20", "azB071JT7QVL", "azB01HR3DOMS", "azB01HR3DOSC", "azB01HR3DQZS", "azB0765TGLGH", "azB0765X7YKV", "azB0765TGLG1", "azB01HR3DOI2", "azB072K1M1TC", "azB079976RPB", "azB0765TGHLY", "azB0765W8XDV", "azB01HR3DR9S", "azB01HR3DOKA"]
# ニコニコ動画のアカウント設定
nicoMail = os.environ["NICONICO_MAIL"]
nicoPW = os.environ["NICONICO_PASS"]

def login(driver, mail, pw):
    driver.get("https://account.nicovideo.jp/login")
    driver.find_element_by_id("input__mailtel").send_keys(mail)
    driver.find_element_by_id("input__password").send_keys(pw)
    driver.find_element_by_id("login__submit").click()
    return driver

def proc_ichiba(bloadcast_url):

    # 【前処理】
    # オプション設定用
    options = Options()
    # GUI起動OFF（=True）
    options.set_headless(True)
    # Chromeドライバを設定
    driver = webdriver.Chrome(chrome_options=options)

    while True:
        try:
            # 【ログイン】
            driver = login(driver, nicoMail, nicoPW)
            break
        except Exception as e:
            logging.warning(e)   

    while True:
        try:
            # 【放送ページへ移動】
            # 視聴ページにアクセスできない場合は、「放送終了」として処理する。
            try:
                driver.get(bloadcast_url)
            except Exception as e:
                logging.info(e)
                
            # 【市場編集を開く】
            while True:
                try:
                    driver.find_element_by_xpath("//*[@id='ichiba_edit_buttonB']/form/input").click()
                    break
                except Exception as e:
                    logging.warning(e)

            # 【不要な商品を削除】
            xPath = "//*[@id='bpn_display_big']/tbody/tr[{}]/td[{}]"
            iTr = 3
            while iTr > 0:
                iTd = 5
                while iTd > 0:
                    try:
                        idItem = driver.find_element_by_xpath(xPath.format(iTr, iTd)).get_attribute("id")[11:]
                        driver.execute_script("ichibaB.deleteItem('" + idItem + "');")
                        sleep(1)
                        logging.info("[DELETE]" + idItem)
                    except Exception as e:
                        try:
                            Alert(driver).accept()
                        except Exception as e1:
                            logging.critical(e1)
                        logging.warning(e)
                    iTd -= 1
                iTr -= 1

            # 【必要な商品を登録】
            for idItem in listItems:
                try:
                    driver.execute_script("ichibaB.addItem('" + idItem + "');")
                    logging.info("[ADD]" + idItem)
                    sleep(1)
                except Exception as e:
                    try:
                        Alert(driver).accept()
                    except Exception as e1:
                        logging.critical(e1)
                    logging.warning(e)

            sleep(15)

        except Exception as e:
            logging.critical(e) 
            while True:
                try:
                    # 【ログイン】
                    driver = login(driver, nicoMail, nicoPW)
                    break
                except Exception as e:
                    logging.warning(e)  

    # 【後処理】
    driver.close()
    driver.quit()
