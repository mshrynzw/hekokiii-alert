import datetime
import logging
import re
import requests
from bs4 import BeautifulSoup
from proc_db import db_connect, db_close, db_insert_message

# DBのテーブル名
tbl_name = "youtube_super_chat"
video_id = "8ViucSjZlPo"


def insert_messages(data):
    # DB接続
    arg = db_connect()
    conn = arg[0]
    cur = arg[1]

    # DB（INSERT文）
    db_insert_message(cur, tbl_name, data)

    # DB切断
    db_close(conn, cur)


def check_message_yt():
    target_url = r"https://www.youtube.com/watch?v=" + video_id
    next_url = ""
    message_data = []
    session = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36'}

    # まず動画ページにrequestsを実行しhtmlソースを手に入れてlive_chat_replayの先頭のurlを入手
    html = requests.get(target_url)
    soup = BeautifulSoup(html.text, "html.parser")

    for iframe in soup.find_all("iframe"):

        if "live_chat_replay" in iframe["src"]:
            next_url = iframe["src"]

    while 1:

        try:
            html = session.get(next_url, headers=headers)
            soup = BeautifulSoup(html.text, "lxml")
            # 次に飛ぶurlのデータがある部分をfind_allで探してsplitで整形
            # for scrp in soup.find_all("script"):
            #     if "window[\"ytInitialData\"]" in scrp.text:
            #         dict_str = scrp.text.split(" = ")[1]

            # 下記内容に修正
            scrp = soup.find_all("script")[9]
            dict_str = scrp.string.split(" = ")[1]

            # javascript表記なので更に整形. falseとtrueの表記を直す
            dict_str = dict_str.replace("false", "False")
            dict_str = dict_str.replace("true", "True")

            # 辞書形式と認識すると簡単にデータを取得できるが, 末尾に邪魔なのがあるので消しておく（「空白2つ + \n + ;」を消す）
            dict_str = dict_str.rstrip("  \n;")
            # 辞書形式に変換
            dics = eval(dict_str)

            # "https://www.youtube.com/live_chat_replay?continuation=" + continue_url が次のlive_chat_replayのurl
            continue_url = \
                dics["continuationContents"]["liveChatContinuation"]["continuations"][0][
                    "liveChatReplayContinuationData"][
                    "continuation"]
            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url

            index = 0
            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                index += 1
                logging.info("------------------" + index + "------------------")
                action_0 = samp["replayChatItemAction"]["actions"][0]

                # メンバー登録の場合
                if "addLiveChatTickerItemAction" in action_0:
                    item = action_0["addLiveChatTickerItemAction"]["item"]
                # 通常メッセージの場合
                elif "addChatItemAction" in action_0:
                    item = action_0["addChatItemAction"]["item"]
                # 例外メッセージの場合
                else:
                    continue

                # Super Chatの場合
                if "liveChatPaidMessageRenderer" in item:
                    live_chat_paid_message_renderer = item["liveChatPaidMessageRenderer"]
                elif "liveChatTickerPaidMessageItemRenderer" in item:
                    live_chat_paid_message_renderer = \
                    item["liveChatTickerPaidMessageItemRenderer"]["showItemEndpoint"]["showLiveChatItemEndpoint"][
                        "renderer"]["liveChatPaidMessageRenderer"]

                else:
                    continue

                # Super Chatの場合
                super_chat_id = live_chat_paid_message_renderer["id"]
                author_external_channel_id = live_chat_paid_message_renderer["authorExternalChannelId"]
                time_stamp = datetime.datetime.fromtimestamp(int(live_chat_paid_message_renderer["timestampUsec"][:-6]))
                purchase_amount = re.sub(r'\D', '', live_chat_paid_message_renderer["purchaseAmountText"]["simpleText"])

                message = {
                    "id": super_chat_id,
                    "author_external_channel_id": author_external_channel_id,
                    "video_id": video_id,
                    "time_stamp": time_stamp,
                    "purchase_amount": purchase_amount
                }

                message_data.append(message)

        # next_urlが入手できなくなったら終わり
        except Exception as e:
            print(e)
            break

        if message_data:
            logging.info(message_data)
            insert_messages(message_data)
        else:
            logging.info("There was no message.")
