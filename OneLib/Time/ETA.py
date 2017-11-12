import time

def pretty_eta(sec):
    time_range = [60, 60, 24, 7, 48]
    time_name = [' s ', ' m ', ' h ', ' d ', ' w ']
    eta = ''
    cur = sec
    for rg, name in zip(time_range, time_name):
        nxt = cur / rg
        cur = cur % rg
        eta = str(cur) + name + eta
        if nxt == 0:
            break
        cur = nxt
    return eta

class Timer(object):
    def __init__(self, num_units):
        self.num_units = float(num_units)

    def start(self):
        self.start_time = time.time()
        self.i = 0



    def eta(self):
        self.cur_tm = time.time()
        self.i += 1
        tm_used = self.cur_tm - self.start_time
        percent = self.i/self.num_units
        eta_sec = int(tm_used * (1-percent)/percent)

        # s = "{:.2f}% , ETA: {:d} sec".format(100*percent, int(eta))
        return pretty_eta(eta_sec)
        # return s
