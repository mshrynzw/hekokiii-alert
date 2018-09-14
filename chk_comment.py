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
from bs4 import BeautifulSoup       # HTMLやXMLファイルからデータを取得するPythonのライブラリ
from datetime import datetime, time
from tw_comment import tweet_comment


def check_comment(bloadcast_id):

    # ニコニコ動画のアカウント設定
    mail = os.environ["NICONICO_MAIL"]
    password = os.environ["NICONICO_PASS"]
    LV = bloadcast_id

    # ログイン
    login_info = {
        "mail_tel": mail,
        "password": password
    }

    # セッションを開始
    session = requests.session()

    # ニコニコ動画のログイン画面に接続
    url_login = "https://secure.nicovideo.jp/secure/login?site=niconico"
    res = session.post(url_login, data=login_info)

    # 放送番組の情報を取得
    res = session.get("http://watch.live.nicovideo.jp/api/getplayerstatus?v=" + LV)
    soup = BeautifulSoup(res.text, "xml")

    try:
        addr = soup.getplayerstatus.ms.addr.string              # コメントサーバのアドレスを取得
        port = int(soup.getplayerstatus.ms.port.string)         # コメントサーバのポートを取得
        thread = int(soup.getplayerstatus.ms.thread.string)     # コメントサーバのスレッドIDを取得
    except AttributeError as e:     #放送終了・ログイン不可の場合、例外発生
        print("AttributeError")
        print(e)
        #★ここで処理終了にさせる

    # コメントサーバへ接続
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((addr, port))
    client.sendall(
        (('<thread thread="%s" version="20061206" res_form="-1000"/>'+chr(0)) % thread).encode())

    # 最初にthreadノード受信
    res = client.recv(2048)     # 一度に受信するデータは、最大でも bufsize （引数）で指定した量
    cnt_comment = 0             # コメントカウント 

    #★グラフ用辞書型
    dic_graph = {}

    # 続けてchatノード（コメント）を受信
    while True:
        try:
            res = client.recv(2048).decode('utf-8') #★絵文字などによりエンコードが失敗するので例外処理が必要
            bs = BeautifulSoup(res, "xml")
            chat = bs.find('chat')
            # num = dict(chat.attrs)['no']    # コメント番号を取得
            cmt_date = int(dict(chat.attrs)['date'])
            cmt_time = datetime.fromtimestamp(cmt_date).time().strftime('%H%M')
            comment = chat.string             # コメントを取得
            print(cmt_time)
            print(comment)
        except:
            continue

        #★グラフの値格納
        if cmt_time in dic_graph:
            dic_graph[cmt_time] += 1
        else:
            
            #グラフの作成
            #★横軸に:を入れたい e.g. 00:00
            if cmt_time.endswith("00") or cmt_time.endswith("30"):
                # figure
                fig = plt.figure()
                ax = fig.add_subplot(1, 1, 1)

                x = np.array(list(dic_graph.keys()))
                y = np.array(list(dic_graph.values()))

                plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
                plt.gca().get_yaxis().set_major_locator(ticker.MaxNLocator(integer=True))
                ax.plot(x, y, linestyle="--", color='#e46409')
                plt.ylim(0, 100)
                
                ax.set_title("Comments")

                plt.gca().spines["right"].set_color("none")
                plt.gca().spines["top"].set_color("none")
                plt.savefig("./tmp/figure.jpg")
                plt.close

                tweet_comment("xxx")
                dic_graph.clear()

            dic_graph[cmt_time] = 1

        print(dic_graph)


        # 放送終了時に無限ループが終了
        if comment == u"/disconnect":
            break
        
        cnt_comment += 1
