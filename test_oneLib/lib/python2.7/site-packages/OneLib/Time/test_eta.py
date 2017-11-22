import ETA
from time import sleep

tm = ETA.Timer(10)
tm.start()
for i in range(10):
    sleep(2)
    print tm.eta()
