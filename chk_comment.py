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
    login_info = {
        "mail_tel": os.environ["NICONICO_MAIL"],
        "password": os.environ["NICONICO_PASS"]
    }

    # コネクションのリトライ数
    connectionRetry = 20

    # セッションを開始
    session = requests.session()
    # ニコニコ動画のログイン画面に接続
    url_login = "https://secure.nicovideo.jp/secure/login?site=niconico"
    res = session.post(url_login, data=login_info)
    # 大手放送の場合、放送番組の取得が即時できないため。
    sleep(20)

    # ニコニコ生放送のサーバへ接続し、放送番組の情報を取得
    for i in range(1, connectionRetry + 1):
        try:
            res = session.get(
                "http://watch.live.nicovideo.jp/api/getplayerstatus?v=" + bloadcast_id)
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
            # 最初にthreadノード受信（一度に受信するデータは、最大でも bufsize （引数）で指定した量）
            res = client.recv(2048)
        except:     # 放送終了・ログイン不可の場合、例外発生
            sleep(5)
        else:
            break

    # グラフ作成の関数
    cnt_comment = 0                             # コメントカウント
    intervalCreateGraph = 15                    # グラフ作成の間隔（分）
    intervalXAxis = 5                           # X軸の間隔（分）
    x = list(range(intervalCreateGraph))        # X軸の個数（「グラフ作成の間隔」に準ずる）
    y = [0] * intervalCreateGraph               # Y軸の初期設定（「グラフ作成の間隔」に準ずる）
    listMinute = [""] * intervalCreateGraph     # コメントをカウントするためのリスト
    listXLabel = [""] * intervalCreateGraph     # X軸ラベルを作成するためのリスト
    flgLabel = 0                                # X軸ラベル用フラグ（開始ラベル -> 0:未作成/1:作成済み）
    iY = -1                                     # リスト変数y用の変数

    # 続けてchatノード（コメント）を受信
    while True:
        try:
            res = client.recv(2048).decode('utf-8')
            bs = BeautifulSoup(res, "xml")
            chat = bs.find('chat')
            comment = chat.string                       # コメント内容を取得
            cmt_date = int(dict(chat.attrs)['date'])    # コメント日時を取得

        except:
            continue

        tmpXLabel = datetime.fromtimestamp(cmt_date).time()   # X軸ラベル用の一時変数

        # X軸用のラベルをすべて作成
        if flgLabel != 1:
            tmpHourMinute = tmpXLabel.strftime('%H%M')
            labelHour = tmpHourMinute[:2]
            labelMinute = tmpHourMinute[2:]
            listXLabel[0] = labelHour + ":" + labelMinute
            for i in range(1, intervalCreateGraph):
                labelMinute = int(labelMinute) + 1
                if labelMinute < 60:
                    if labelMinute % intervalXAxis == 0:
                        listXLabel[i] = labelHour + ":" + \
                            str(labelMinute).zfill(2)
                else:
                    if labelMinute % intervalXAxis == 0:
                        tmpHour = int(labelHour) + 1
                        tmpMinute = labelMinute - 60
                        if tmpHour < 24:
                            listXLabel[i] = str(tmpHour) + \
                                ":" + str(tmpMinute).zfill(2)
                        else:
                            tmpHour = 0
                            listXLabel[i] = str(tmpHour) + ":" + str(tmpMinute)

            flgLabel = 1

        # グラフの値格納
        tmpMinute = tmpXLabel.strftime('%M')  # 比較用の変数（分）
        # すでに同時刻（分）にコメントがある場合
        if tmpMinute in listMinute:
            y[iY] += 1
        # すでに同時刻（分）にコメントがない場合
        else:
            # iYが「-1」ではなく、さらに直近時刻取得との差が1分より大きい場合、iYを1増加
            if iY != -1:
                diff = int(tmpMinute) - int(listMinute[iY])
                if diff >= 1:
                    for i in range(diff - 1):
                        iY += 1

            # グラフ作成の間隔がiYと同じ場合、グラフの作成
            if iY == intervalCreateGraph:
                # グラフ設定
                plt.figure()                                        # グラフを初期化             
                matplotlib.rcParams['axes.xmargin'] = 0             # X軸の最小値を設定
                matplotlib.rcParams['axes.ymargin'] = 0             # Y軸の最小値を設定
                plt.plot(x, y, linestyle="-", color='#e46409')      # プロットと線を設定
                plt.ylim(0, 50)                                     # Y軸の最大値を設定
                plt.gca().spines["right"].set_color("none")         # グラフ右の線を削除
                plt.gca().spines["top"].set_color("none")           # グラフ上の線を削除
                plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(25))   # グリッド線設定
                plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(5))    # グリッド線設定
                plt.xticks(x, listXLabel)                           # X軸のラベルを設定
                plt.title("Arena")                                  # グラフのタイトルを設定
                plt.xlabel("time")                                  # X軸のラベルを設定
                plt.ylabel("comments")                              # Y軸のラベルを設定
                plt.grid(True)                                      # グリット線の表示を設定
                # グラフを画像ファイルで出力 
                plt.savefig("./tmp/figure.png")
                # グラフオブジェクトを閉じる
                plt.close

                # グラフの画像ファイルをツイート
                tweet_comment(bloadcast_id)

                #リストを初期化
                y = [0] * intervalCreateGraph
                iY = 0
                flgLabel = 0
                listMinute = [""] * intervalCreateGraph
                listXLabel = [""] * intervalCreateGraph

            # iYのコメント数を1増加
            y[iY] += 1
            listMinute[iY] = tmpMinute

        # コンソールに毎分コメント数を出力
        print(str(listMinute[iY]) + "：" + str(y[iY]))

        # 放送終了時に無限ループが終了
        if comment == u"/disconnect":
            break

        # 総コメント数を1増加
        cnt_comment += 1
