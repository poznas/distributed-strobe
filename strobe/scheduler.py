import sched
import threading
import time

from datetime import datetime
from typing import List


def time_ms():
    return time.time_ns() // 1_000_000


def sleep_ms(ms):
    time.sleep(ms / 1000)


scheduler = sched.scheduler(time_ms, sleep_ms)
events = []


def register_tasks(start_time_ms: float, offsets: List[int], action):
    date_str = datetime.fromtimestamp(start_time_ms // 1000)
    print(f"▶ register_tasks [start_time: {date_str}, offsets.length: {len(offsets)}]")

    def register(offset: int):
        scheduler.enterabs(start_time_ms + offset, 1, action, ())

    events.extend(list(map(register, offsets)))


def purge():
    print("❌ purge events")
    for event in events:
        try:
            scheduler.cancel(event)
        except ValueError:
            pass
    events.clear()


def launch() -> threading.Thread:
    print("▶ run scheduler")
    t = threading.Thread(target=scheduler.run)
    t.start()
    return t
