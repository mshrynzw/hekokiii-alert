import threading
from chk_start import check_start_live
from chk_reserve import check_reserve_live

if __name__ == "__main__":
    thread_1 = threading.Thread(target=check_start_live)
    thread_2 = threading.Thread(target=check_reserve_live)
    thread_1.start()
    thread_2.start()
