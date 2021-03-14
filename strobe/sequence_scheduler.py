import os
import sched
import signal
import threading
import time
from datetime import datetime
from multiprocessing import Process
from typing import List

from util.logger import logger


def time_ms():
    return time.time_ns() // 1_000_000


def sleep_ms(ms):
    time.sleep(ms / 1000)


def run_scheduler(scheduler):
    logger.info("▶ run scheduler")
    os.nice(-20)
    scheduler.run()


class SequenceScheduler:
    _scheduler = sched.scheduler(time_ms, sleep_ms)
    _events = []
    _pid = 0

    def register_task(self, start_time_ms: float, action):
        self.register_tasks(start_time_ms, [0] * 1, action)


    def register_tasks(self, start_time_ms: float, offsets: List[int], action):
        date_str = datetime.fromtimestamp(start_time_ms // 1000)
        logger.info(
            f"▶ register_tasks [start_time: {date_str}, offsets.length: {len(offsets)}, fun: {action.__name__}]"
        )

        def register(offset: int):
            return self._scheduler.enterabs(start_time_ms + offset, 1, action, ())

        self._events.extend(list(map(register, offsets)))


    def purge(self):
        if self._pid == 0:
            return

        try:
            for event in self._events:
                try:
                    self._scheduler.cancel(event)
                except ValueError:
                    pass
            try:
                os.kill(self._pid, signal.SIGKILL)
            except ProcessLookupError as e:
                logger.warn(e)
        finally:
            self._pid = 0
            self._events.clear()
            logger.info("❌ purge events")


    def launch(self):
        if self._pid != 0:
            return

        t = threading.Thread(target=self.spawn_scheduler)
        t.start()


    def spawn_scheduler(self):
        process = Process(target=run_scheduler, args=(self._scheduler,))
        process.start()
        self._pid = process.pid
        process.join()
        self.purge()


    def empty(self) -> bool:
        return self._scheduler.empty()
