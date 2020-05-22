import os
import threading
from chk_start import check_start_live
from chk_reserve import check_reserve_live
from chk_notice import check_notice
# from chk_movie import check_movie
# from chk_bbs import check_bbs
# from chk_reserve_yt import check_reserve_yt
from chk_start_yt import check_start_yt
from chk_message_yt import select_all_messages
from chk_twitter import check_twitter


if __name__ == "__main__":

    if os.environ["IS_NICONICO"]:
        thread_1 = threading.Thread(target=check_start_live)
        thread_2 = threading.Thread(target=check_reserve_live)
        thread_3 = threading.Thread(target=check_notice)
        thread_1.start()
        thread_2.start()
        thread_3.start()

    if os.environ["IS_YOUTUBE"]:
        # thread_4 = threading.Thread(target=check_movie)
        # thread_5 = threading.Thread(target=check_reserve_yt)
        thread_6 = threading.Thread(target=check_start_yt)
        thread_60 = threading.Thread(target=select_all_messages)
        # thread_4.start()
        # thread_5.start()
        thread_6.start()
        thread_60.start()

    if os.environ["IS_TWITTER"]:
        thread_7 = threading.Thread(target=check_twitter)
        thread_7.start()

    # if os.environ["IS_BBS"]:
        # thread_8 = threading.Thread(target=check_bbs)
        # thread_8.start()
