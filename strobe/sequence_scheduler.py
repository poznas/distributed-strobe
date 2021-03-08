import os
import sched
import threading
import time

from datetime import datetime
from typing import List

from util.logger import logger


def time_ms():
    return time.time_ns() // 1_000_000


def sleep_ms(ms):
    time.sleep(ms / 1000)


scheduler = sched.scheduler(time_ms, sleep_ms)
events = []


def register_tasks(start_time_ms: float, offsets: List[int], action):
    date_str = datetime.fromtimestamp(start_time_ms // 1000)
    print(f"▶ register_tasks [start_time: {date_str}, offsets.length: {len(offsets)}, fun: {action.__name__}]")

    def register(offset: int):
        return scheduler.enterabs(start_time_ms + offset, 1, action, ())

    events.extend(list(map(register, offsets)))


def sequence_purge():
    try:
        for event in events:
            try:
                scheduler.cancel(event)
            except ValueError:
                pass
    finally:
        events.clear()
        logger.info("❌ purge events")


def sequence_launch() -> threading.Thread:

    def run_scheduler():
        logger.info("▶ run scheduler")
        os.nice(-20)
        scheduler.run()

    t = threading.Thread(target=run_scheduler)
    t.start()
    return t


def sequence_scheduler_empty() -> bool:
    return scheduler.empty()
