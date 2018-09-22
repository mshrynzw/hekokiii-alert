import threading
from chk_start import check_start_live
from chk_reserve import check_reserve_live
from chk_comment import check_comment

if __name__ == "__main__":
    thread_1 = threading.Thread(target=check_start_live)
    thread_2 = threading.Thread(target=check_reserve_live)
    thread_3 = threading.Thread(target=check_comment, args=("315809551",))
    thread_1.start()
    thread_2.start()
    thread_3.start()
