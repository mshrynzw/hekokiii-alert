import threading
from chk_start import check_start_live
from chk_reserve import check_reserve_live
from chk_notice import check_notice
from chk_movie import check_movie
from chk_bbs import check_bbs
from chk_reserve_yt import check_reserve_yt

if __name__ == "__main__":
    thread_1 = threading.Thread(target=check_start_live)
    thread_2 = threading.Thread(target=check_reserve_live)
    thread_3 = threading.Thread(target=check_notice)
    thread_4 = threading.Thread(target=check_movie)
    thread_5 = threading.Thread(target=check_bbs)
    thread_6 = threading.Thread(target=check_reserve_yt)
    thread_1.start()
    thread_2.start()
    thread_3.start()
    thread_4.start()
    thread_5.start()
    thread_6.start()
    
