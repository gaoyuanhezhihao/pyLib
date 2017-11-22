from __future__ import print_function
from OneLib.Time.ETA import Timer
import time

tm = Timer(10)
tm.start()
for i in range(10):
    time.sleep(1)
    print(tm.eta())

