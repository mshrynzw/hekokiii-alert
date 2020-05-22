import datetime
import logging
import re
import requests
import traceback
from bs4 import BeautifulSoup
from proc_db import db_insert_user, db_insert_paid_chat, db_insert_chat_text, db_select_all_videos, \
    db_select_user_id_list, db_update_video_has_got_messages


def check_message_yt(video):
    retry_times = 0
    next_url = ""
    paid_chat_data = []
    chat_text_data = []

    user_id_list = db_select_user_id_list()

    target_url = r"https://www.youtube.com/watch?v=" + video
    session = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/69.0.3497.100 Safari/537.36'}

    # まず動画ページにrequestsを実行しhtmlソースを手に入れてlive_chat_replayの先頭のurlを入手
    html = requests.get(target_url)
    soup = BeautifulSoup(html.text, "html.parser")

    for iframe in soup.find_all("iframe"):

        if "live_chat_replay" in iframe["src"]:
            next_url = requests.compat.urljoin(r"https://www.youtube.com/", iframe["src"])

    while True:

        try:
            try:
                html = session.get(next_url, headers=headers)
            except requests.exceptions.MissingSchema:
                retry_times += 1
                if retry_times <= 10:
                    logging.info("Retry times: " + str(retry_times))
                    continue
                else:
                    logging.error("Over max retry times")
                    break

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
            continuation = dics["continuationContents"]["liveChatContinuation"]["continuations"][0]
            if not ("liveChatReplayContinuationData" in continuation):
                logging.info("There was not liveChatReplayContinuationData. (video_id: " + video + ")")
                db_update_video_has_got_messages(video)
                break

            continue_url = continuation["liveChatReplayContinuationData"]["continuation"]
            next_url = "https://www.youtube.com/live_chat_replay?continuation=" + continue_url

            # dics["continuationContents"]["liveChatContinuation"]["actions"]がコメントデータのリスト。先頭はノイズデータなので[1:]で保存
            for samp in dics["continuationContents"]["liveChatContinuation"]["actions"][1:]:
                action_0 = samp["replayChatItemAction"]["actions"][0]

                # メッセージの場合
                if "addChatItemAction" in action_0:
                    item = action_0["addChatItemAction"]["item"]

                    # Paid Chatの場合
                    if "liveChatPaidMessageRenderer" in item:
                        live_chat_paid_message_renderer = item["liveChatPaidMessageRenderer"]

                        if not ("message" in live_chat_paid_message_renderer):
                            continue

                        runs = live_chat_paid_message_renderer["message"]["runs"]
                        message = ''
                        for run in runs:
                            if "text" in run:
                                message += run["text"]

                        super_chat_id = live_chat_paid_message_renderer["id"]
                        author_external_channel_id = live_chat_paid_message_renderer["authorExternalChannelId"]
                        time_stamp = datetime.datetime.fromtimestamp(
                            int(live_chat_paid_message_renderer["timestampUsec"][:-6]))
                        video_time_stamp = live_chat_paid_message_renderer["timestampText"]["simpleText"]

                        # 日本円のみ対応
                        simple_text = live_chat_paid_message_renderer["purchaseAmountText"]["simpleText"]
                        if simple_text.startswith(r"¥"):
                            purchase_amount = re.sub(r'\D', '', simple_text)

                            paid_chat = {
                                "id": super_chat_id,
                                "author_external_channel_id": author_external_channel_id,
                                "video_id": video,
                                "time_stamp": time_stamp,
                                "video_time_stamp": video_time_stamp,
                                "purchase_amount": purchase_amount
                            }
                            paid_chat_data.append(paid_chat)

                        chat_text = {
                            "id": super_chat_id,
                            "author_external_channel_id": author_external_channel_id,
                            "video_id": video,
                            "time_stamp": time_stamp,
                            "video_time_stamp": video_time_stamp,
                            "message": message
                        }
                        chat_text_data.append(chat_text)

                        # ユーザー追加
                        if not (author_external_channel_id in user_id_list):
                            db_insert_user(
                                author_external_channel_id,
                                live_chat_paid_message_renderer["authorName"]["simpleText"]
                            )
                            user_id_list.append(author_external_channel_id)

                    # Chat Textの場合
                    elif "liveChatTextMessageRenderer" in item:
                        live_chat_text_message_renderer = item["liveChatTextMessageRenderer"]

                        if not ("message" in live_chat_text_message_renderer):
                            continue

                        runs = live_chat_text_message_renderer["message"]["runs"]
                        message = ''
                        for run in runs:
                            if "text" in run:
                                message += run["text"]

                        chat_id = live_chat_text_message_renderer["id"]
                        author_external_channel_id = live_chat_text_message_renderer["authorExternalChannelId"]
                        time_stamp = datetime.datetime.fromtimestamp(
                            int(live_chat_text_message_renderer["timestampUsec"][:-6]))
                        video_time_stamp = live_chat_text_message_renderer["timestampText"]["simpleText"]

                        chat_text = {
                            "id": chat_id,
                            "author_external_channel_id": author_external_channel_id,
                            "video_id": video,
                            "time_stamp": time_stamp,
                            "video_time_stamp": video_time_stamp,
                            "message": message
                        }
                        chat_text_data.append(chat_text)

                        # ユーザー追加
                        if not (author_external_channel_id in user_id_list):
                            db_insert_user(
                                author_external_channel_id,
                                live_chat_text_message_renderer["authorName"]["simpleText"]
                            )
                            user_id_list.append(author_external_channel_id)

                    else:
                        continue

                # 例外メッセージの場合
                else:
                    continue

        except Exception as e:
            logging.error(e)
            logging.error(traceback.print_exc())
            break

    if paid_chat_data:
        db_insert_paid_chat(paid_chat_data)
    else:
        logging.info("There was no Super Chat. (video_id: " + video + ")")

    if chat_text_data:
        db_insert_chat_text(chat_text_data)
    else:
        logging.info("There was no message. (video_id: " + video + ")")


def select_all_messages():
    # DB（INSERT文）
    videos = db_select_all_videos()

    for video in videos:
        logging.info("Start check message.  (video_id: " + video + ")")
        check_message_yt(video)
        logging.info("Finish check message. (video_id: " + video + ")")
