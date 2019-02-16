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
# ニコニコ動画のアカウント設定
nicoMail = os.environ["NICONICO_MAIL"]
nicoPW = os.environ["NICONICO_PASS"]
# 処理の回数と期間
ICHIBA_TIMES = int(os.environ["ICHIBA_TIMES"])
ICHIBA_TERM_S = int(os.environ["ICHIBA_TERM_S"])
# 特定の商品を設定
strItems = os.environ["ICHIBA_ITEMS"]
listItems = strItems.split(",")

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
    ## Chromeドライバを設定
    driver = webdriver.Chrome(chrome_options=options)
    
    ## PhantomJSのドライバ設定
    # driver = webdriver.PhantomJS()

    while True:
        try:
            # 【ログイン】
            driver = login(driver, nicoMail, nicoPW)
            break
        except Exception as e:
            logging.warning(e)   

    # 処理カウント用変数
    procTimes = 0

    while procTimes < ICHIBA_TIMES:
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
                    ## driver.find_element_by_xpath("//*[@id='ichiba_edit_buttonB']/form/input").click()
                    driver.execute_script("ichibaB.showIchibaConsole('az');")
                    sleep(5)
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
                        sleep(3)
                        logging.info("[DELETE]" + idItem)
                    except Exception as e:
                        try:
                            Alert(driver).accept()
                        except Exception as e1:
                            logging.warning(e1)
                        logging.warning(e)
                    iTd -= 1
                iTr -= 1

            # 【必要な商品を登録】
            for idItem in listItems:
                try:
                    driver.execute_script("ichibaB.addItem('" + idItem + "');")
                    logging.info("[ADD]" + idItem)
                    sleep(3)
                except Exception as e:
                    try:
                        Alert(driver).accept()
                    except Exception as e1:
                        logging.critical(e1)
                    logging.warning(e)
                    continue

            # 【スリープ】
            sleep(ICHIBA_TERM_S)
            # 処理カウント+1
            procTimes +=1

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
