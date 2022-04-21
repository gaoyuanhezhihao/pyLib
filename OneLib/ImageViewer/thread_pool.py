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
        # with self.condition:
        if self.job_queue.empty():
            return False
        else:
            # print('getting:', i)
            self.job_buf[i] = self.job_queue.get()
            # print('got:', i)
            return True

    def clear_job_queue(self):
        with self.condition:
            for _ in range(self.job_queue.qsize()):
                job = self.job_queue.get()
                job.complete()



    def thread_main(self, i):
        # print(i, '-thread start')
        while not self.exit:
            with self.condition:
                self.condition.wait_for(partial(self.try_get_one_job, i))
            if self.exit:
                break;
            try:
                self.job_buf[i]()
            except Exception as e:
                print(e)
                exit()
        # print('exit,', i)

    def add_job(self, job_func):
        with self.condition:
            self.job_queue.put(job_func)
            self.condition.notify_all()

    def stop(self):
        with self.condition:
            self.exit = True
            self.condition.notify_all()
        for t in self.threads:
            t.join()

class A:
    def work(self, i):
        print(i)

    def run(self):
        thread_pool = ThreadPool(4)
        for i in range(2000):
            thread_pool.add_job(partial(self.work, i))


from time import sleep
if __name__ == '__main__':
    # thread_pool = ThreadPool(4)
    # for i in range(2000):
        # thread_pool.add_job(partial(print, i))
    # sleep(10)
    a = A()
    a.run()

