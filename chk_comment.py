#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
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

# *** 運用モード ***
# - PROD ：本番
# - TEST1：テスト（chk_comment.py以外）
# - TEST2：テスト（chk_comment.pyのみ）
MODE_SETTING = os.environ["MODE_SETTING"]

# コネクションのリトライ数
CRT = int(os.environ["CONNECTION_RETRY_TIMES"])
# ニコニコ動画のアカウント設定
LI = {
    "mail_tel": os.environ["NICONICO_MAIL"],
    "password": os.environ["NICONICO_PASS"]
}
# ツイートのテンプレート
strTweet = os.environ["TWEET_TPL_COMMENT"]


def check_comment(bloadcast_url):
    # テストの場合は放送IDを変更
    if MODE_SETTING == "TEST2":
        bloadcast_id = os.environ["NICONICO_BLOADCAST_URL_TEST2"]
    # 放送URLから放送IDを抽出
    bloadcast_id = bloadcast_url[32:]
    
    # セッションを開始
    session = requests.session()
    # ニコニコ動画のログイン画面に接続
    url_login = "https://secure.nicovideo.jp/secure/login?site=niconico"
    res = session.post(url_login, data=LI)
    # 大手放送の場合、放送番組の取得が即時できないため。
    sleep(20)

    # ニコニコ生放送のサーバへ接続し、放送番組の情報を取得
    for i in range(1, CRT + 1):
        try:
            res = session.get(
                "http://watch.live.nicovideo.jp/api/getplayerstatus?v=" + bloadcast_id)
            soup = BeautifulSoup(res.text, "lxml")
            addr = soup.getplayerstatus.ms.addr.string              # コメントサーバのアドレスを取得
            port = int(soup.getplayerstatus.ms.port.string)         # コメントサーバのポートを取得
            thread = int(soup.getplayerstatus.ms.thread.string)     # コメントサーバのスレッドIDを取得
            print("★")
        except:     #放送終了・ログイン不可の場合、例外発生
            sleep(5)
            break

    for i in range(1, CRT + 1):
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
    xAxisCount = 25                    # X軸の個数（15分毎 * 6時間 +1）
    intervalXAxis = 4                  # X軸ラベルの間隔（1時間毎）
    x = list(range(xAxisCount))        # X軸の個数（「グラフ作成の間隔」に準ずる）
    y = [0] * xAxisCount               # Y軸の初期設定（「グラフ作成の間隔」に準ずる）
    yOceanLeaf = [0] * xAxisCount      # 「海」のためのY軸の初期設定（「グラフ作成の間隔」に準ずる）
    listXLabel = [""] * xAxisCount     # X軸ラベルを作成するためのリスト
    isLabel = False                    # X軸ラベル用フラグ
    stage15M = 0                       # 時刻0-14分の場合「0」、15-29分の場合「1」、30-44分の場合「2」、45-59分の場合「3」
    isStage15M = False                 # 15分段階設定の完了フラグ
    iY = 1                             # リスト変数y用の変数

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

        tmpOcean = comment.count("海")                        # コメントから「海」の個数を検索
        tmpLeaf = comment.count("w")                         # コメントから「w」の個数を検索
        tmpXLabel = datetime.fromtimestamp(cmt_date).time()   # X軸ラベル用の一時変数

        tmpHourMinute = tmpXLabel.strftime('%H%M')
        tmpMinute = int(tmpHourMinute[2:])

        # X軸用のラベルをすべて作成
        if not isLabel:
            tmpHour = tmpHourMinute[:2]
            listXLabel[0] = tmpHour + ":" + str((tmpMinute // 15) * 15 ).zfill(2)
            for i in range(intervalXAxis - tmpMinute // 15, xAxisCount, intervalXAxis):
                tmpHour = int(tmpHour) + 1
                listXLabel[i] = str(tmpHour) + ":00"
                if i in (2, 3): # ラベルの重なり表示対策
                    listXLabel[0] = ""
            isLabel = True
        
        tmpStage15M = math.floor(tmpMinute / 15)
        
        # 初回コメント時に設定
        if not isStage15M:
            stage15M = tmpStage15M
            isStage15M = True
        
        # グラフを作成する場合
        if tmpStage15M != stage15M or comment == u"/disconnect":

            # 前処理
            plt.figure()                                    # グラフを初期化
            matplotlib.rcParams['axes.ymargin'] = 0         # Y軸の最小値を設定

            # 「海・草」数（Y軸右）を出力
            fig, ax1 = plt.subplots()
            ax1.bar(x, yOceanLeaf, color="#258d8d", width=0.5)    # 棒グラフのプロットを設定
            ax1.set_ylabel("Ocean & Leaf", color="#258d8d")        # Y軸のラベルを設定
            ax1.set_ylim(0, 60)                            # Y軸の最大値を設定
            fig.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))    # グリッド線設定

            # コメント数（Y軸左）を出力
            ax2 = ax1.twinx()
            ax2.plot(x, y, color="#d9a300")     # 折れ線グラフのプロットと線を設定
            ax2.set_ylabel("Comment", color="#d9a300")
            ax2.set_ylim(0, 600)                        
            fig.gca().yaxis.set_major_locator(ticker.MultipleLocator(100))    # グリッド線設定

            # グラフ設定
            fig.gca().spines["top"].set_color("none")       # グラフ上の線を削除
            plt.xticks(x, listXLabel)                       # X軸のラベルを設定
            plt.title("Arena")                              # グラフのタイトルを設定
            plt.xlabel("time")                              # X軸のラベルを設定
            plt.grid(True)                                  # グリット線の表示を設定
            fig.savefig("./tmp/figure.png")                 # グラフを画像ファイルで出力
            
            # グラフオブジェクトを閉じる
            plt.close()

                        # 放送終了時に無限ループが終了
            if comment == u"/disconnect":
                tweet_comment(strTweet.format("放送終了", bloadcast_id))
                break

            # グラフの画像ファイルをツイート
            tweet_comment(strTweet.format("放送中", bloadcast_id))

            # インデックス増加
            iY += 1
            stage15M = tmpStage15M

        # iYのコメント数を1増加
        y[iY] += 1
        yOceanLeaf[iY] += tmpOcean
        yOceanLeaf[iY] += tmpLeaf
