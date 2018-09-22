#!/usr/bin/python
# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
import requests
import socket
from bs4 import BeautifulSoup
from datetime import datetime, time
from time import sleep
from tw_comment import tweet_comment


def check_comment(bloadcast_id):

    # ニコニコ動画のアカウント設定
    mail = os.environ["NICONICO_MAIL"]
    password = os.environ["NICONICO_PASS"]

    # ログイン
    login_info = {
        "mail_tel": mail,
        "password": password
    }

    # コネクションのリトライ数
    connectionRetry = 20

    # セッションを開始
    session = requests.session()

    # ニコニコ動画のログイン画面に接続
    url_login = "https://secure.nicovideo.jp/secure/login?site=niconico"
    res = session.post(url_login, data=login_info)

    # 大手放送の場合、放送番組の取得が即時できないため。
    sleep(60)

    # ニコニコ生放送のサーバへ接続し、放送番組の情報を取得
    for i in range(1, connectionRetry + 1):
        try:
            res = session.get("http://watch.live.nicovideo.jp/api/getplayerstatus?v=" + bloadcast_id)
            soup = BeautifulSoup(res.text, "lxml")
            addr = soup.getplayerstatus.ms.addr.string              # コメントサーバのアドレスを取得
            port = int(soup.getplayerstatus.ms.port.string)         # コメントサーバのポートを取得
            thread = int(soup.getplayerstatus.ms.thread.string)     # コメントサーバのスレッドIDを取得
        except:     #放送終了・ログイン不可の場合、例外発生
            sleep(5)
        else:
            break

    for i in range(1, connectionRetry + 1):
        try:
            # コメントサーバへ接続
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((addr, port))
            client.sendall((('<thread thread="%s" version="20061206" res_form="-1000"/>'+chr(0)) % thread).encode())
            # 最初にthreadノード受信
            res = client.recv(2048)     # 一度に受信するデータは、最大でも bufsize （引数）で指定した量
        except:
            sleep(5)
        else:
            break

    # コメントカウント
    cnt_comment = 0
    # グラフ作成の関数
    intervalCreateGraph = 15
    intervalXAxis = 5
    x = list(range(intervalCreateGraph))
    y = [0] * intervalCreateGraph
    listMinute = [""] * intervalCreateGraph  # コメントをカウントするための分リスト
    listLabel = [""] * intervalCreateGraph  # X軸ラベルを作成するための分リスト
    flgLabel = 0    # x軸ラベル用フラグ（開始ラベル -> 0:未取得/1:取得済み）
    iY = -1        # 「コメント数0の場合、yに0を格納」用フラグ

    # 続けてchatノード（コメント）を受信
    while True:
        try:
            # ★絵文字などによりエンコードが失敗するので例外処理が必要
            res = client.recv(2048).decode('utf-8')
            bs = BeautifulSoup(res, "xml")
            chat = bs.find('chat')
            # num = dict(chat.attrs)['no']    # コメント番号を取得
            comment = chat.string             # コメントを取得
            cmt_date = int(dict(chat.attrs)['date'])

        except:
            continue

        flgLabelTmp = datetime.fromtimestamp(cmt_date).time()   # 複数箇所で使用する変数

        # X軸用のラベルをすべて作成
        if flgLabel != 1:
            tmpHourMinute = flgLabelTmp.strftime('%H%M')
            labelHour = tmpHourMinute[:2]
            labelMinute = tmpHourMinute[2:]
            listLabel[0] = labelHour + ":" + labelMinute
            for i in range(1, intervalCreateGraph):
                labelMinute = int(labelMinute) + 1
                if labelMinute < 60:
                    if labelMinute % intervalXAxis == 0:
                        listLabel[i] = labelHour + ":" + \
                            str(labelMinute).zfill(2)
                else:
                    if labelMinute % intervalXAxis == 0:
                        tmpHour = int(labelHour) + 1
                        tmpMinute = labelMinute - 60
                        if tmpHour < 24:
                            listLabel[i] = str(tmpHour) + \
                                ":" + str(tmpMinute).zfill(2)
                        else:
                            tmpHour = 0
                            listLabel[i] = str(tmpHour) + ":" + str(tmpMinute)

            flgLabel = 1

        #cmt_time = datetime.fromtimestamp(cmt_date).time().strftime('%H%M')

        #★グラフの値格納
        tmpMinute = flgLabelTmp.strftime('%M')  # 　比較用の分変数
        if tmpMinute in listMinute:
            y[iY] += 1
        else:

            # コメント数0の場合、yに0を格納
            if iY != -1:
                diff = int(tmpMinute) - int(listMinute[iY])
                if diff > 1:
                    for i in range(diff - 1):
                        iY += 1

            iY += 1

            #グラフの作成
            if iY >= intervalCreateGraph:

                matplotlib.rcParams['axes.xmargin'] = 0
                matplotlib.rcParams['axes.ymargin'] = 0
                plt.plot(x, y, linestyle="-", color='#e46409')     # プロットと線を設定
                plt.ylim(0, 75)                                     # Y軸の最大値を設定
                plt.gca().spines["right"].set_color("none")
                plt.gca().spines["top"].set_color("none")
                plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(25))
                plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(5))

                #for i in range(len(x)):
                #    if x[i] % 5 != 0:
                #        listMinute[i] = ""

                plt.xticks(x, listLabel)
                plt.title("Arena")
                plt.xlabel("time")
                plt.ylabel("comments")
                plt.grid(True)
                plt.savefig("./tmp/figure.png")
                plt.close

                #★tweet_comment(bloadcast_id)

                #リストを初期化
                y = [0] * intervalCreateGraph
                iY = 0
                listMinute = [""] * intervalCreateGraph
                listLabel = [""] * intervalCreateGraph

            y[iY] += 1
            listMinute[iY] = tmpMinute

        print(str(listMinute[iY]) + "：" + str(y[iY]))

        # 放送終了時に無限ループが終了
        if comment == u"/disconnect":
            break

        cnt_comment += 1


if __name__ == '__main__':

    check_comment("lv315743664")
