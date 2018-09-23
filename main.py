import threading
from rq import Queue
from worker import conn
from bottle import route, run
from chk_start import check_start_live
from chk_reserve import check_reserve_live

q = Queue(connection=conn)

@route('/index')
def index():
    result = q.enqueue(background_process, '引数１')
    return result

def background_process(name):
    # ここに時間のかかる処理を書く
    if __name__ == "__main__":
        thread_1 = threading.Thread(target=check_start_live)
        thread_2 = threading.Thread(target=check_reserve_live)
        thread_1.start()
        thread_2.start()
    return name * 10


run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
