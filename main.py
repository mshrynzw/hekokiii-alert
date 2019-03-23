import threading
from chk_start import check_start_live
from chk_reserve import check_reserve_live
from chk_notice import check_notice
from chk_movie import check_movie

if __name__ == "__main__":
    thread_1 = threading.Thread(target=check_start_live)
    thread_2 = threading.Thread(target=check_reserve_live)
    thread_3 = threading.Thread(target=check_notice)
    # thread_4 = threading.Thread(target=check_movie)
    thread_1.start()
    thread_2.start()
    thread_3.start()
    # thread_4.start()
