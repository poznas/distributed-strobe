from typing import List

from blink import setup_blinkers, cleanup_blinkers, blink
from scheduler import register_tasks, launch, purge

NodeID = str


class StrobeNode(object):
    sequence: List[int] = []

    def register_tasks(self, start_time_ms: float):
        setup_blinkers()
        register_tasks(start_time_ms, self.sequence, blink)
        return self

    def start(self):
        launch().join()

    def stop(self):
        purge()
        cleanup_blinkers()
