import time

with open("/tmp/timer_time", "w") as f:
    f.write(str(time.time()))
