#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import http.cookiejar
import socket
import os
import xmltodict
from alert_tweet import alert_tweet

# ニコニコ動画のアカウント設定
mail = os.environ["NICONICO_MAIL"]
password = os.environ["NICONICO_PASS"]
community_id = os.environ["NICONICO_COMMUNITY_ID"]


# ログインAPIその1に接続
opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
urllib.request.install_opener(opener)
res = urllib.request.urlopen("https://secure.nicovideo.jp/secure/login?site=nicolive_antenna",
                             urllib.parse.urlencode({"mail": mail, "password": password}).encode('ascii'))
res_data = xmltodict.parse(res.read().decode('utf-8'))
ticket = res_data["nicovideo_user_response"]["ticket"]

# 認証APIその2に接続
res = urllib.request.urlopen("http://live.nicovideo.jp/api/getalertstatus",
                             urllib.parse.urlencode({"ticket": ticket}).encode('ascii'))
res_data = xmltodict.parse(res.read().decode('utf-8'))

# コメントサーバーに接続
host = res_data["getalertstatus"]["ms"]["addr"]
port = int(res_data["getalertstatus"]["ms"]["port"])
thread = res_data["getalertstatus"]["ms"]["thread"]
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
client.sendall(
    (('<thread thread="%s" version="20061206" res_form="-1"/>'+chr(0)) % thread).encode())

# 該当のコミュニティの放送開始を監視
while True:

    res = client.recv(1024).decode('utf-8')

    if community_id in res:

        bloadcast_id = res.split(",")[0].split(">")[1]
        alert_tweet(bloadcast_id)
