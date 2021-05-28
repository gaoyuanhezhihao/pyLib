from threading import Thread, Condition
from queue import Queue
from functools import partial

class ThreadPool:

    def __init__(self, num_thread):
        self.condition = Condition()
        self.exit = False
        self.job_queue = Queue()
        self.job_buf = [None for _ in range(num_thread)]
        self.threads = [Thread(target=self.thread_main, args = (i,)) for i in range(num_thread)]
        for t in self.threads:
            t.start()

    def try_get_one_job(self, i):
        if self.exit:
            return True
        self.condition.acquire()
        if self.job_queue.empty():
            self.condition.release()
            return False
        else:
            self.job_buf[i] = self.job_queue.get()
            self.condition.release()
            return True


    def thread_main(self, i):
        print(i, '-thread start')
        while not self.exit:
            with self.condition:
                self.condition.wait_for(partial(self.try_get_one_job, i))
            if self.exit:
                break;
            self.job_buf[i]()

    def add_job(self, job_func):
        self.condition.acquire()
        self.job_queue.put(job_func)
        self.condition.notify()
        self.condition.release()



from time import sleep
if __name__ == '__main__':
    thread_pool = ThreadPool(4)
    for i in range(20):
        thread_pool.add_job(partial(print, i))
    sleep(10)

