from enum import Enum
from typing import List

from strobe.blink import setup_blinkers, blink, cleanup_blinkers
from strobe.sequence_scheduler import register_tasks, sequence_launch, sequence_purge

NodeID = str


class StrobeNode(object):
    sequence: List[int] = []

    def register_tasks(self, start_time_ms: float):
        setup_blinkers()
        register_tasks(start_time_ms, self.sequence, blink)
        return self

    def start(self):
        sequence_launch()

    def stop(self):
        sequence_purge()
        cleanup_blinkers()


class NodeStatus(Enum):
    ACTIVE = 'ACTIVE'
    LOST = 'LOST'
