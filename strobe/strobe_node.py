import os

from enum import Enum
from typing import List

from strobe.blink import setup_blinkers, blink, cleanup_blinkers
from strobe.sequence_scheduler import SequenceScheduler

NodeID = str

MIN_EXECUTION_WAIT_TIME = os.getenv('MIN_EXECUTION_WAIT_TIME', 10)


class StrobeNode(object):
    _sequence: List[int] = []
    _sequence_scheduler: SequenceScheduler = SequenceScheduler()


    def register_tasks(self, start_time_ms: float):
        setup_blinkers()
        self._sequence_scheduler.register_tasks(start_time_ms, self._sequence, blink)
        return self

    def start(self):
        self._sequence_scheduler.launch()

    def stop(self):
        self._sequence_scheduler.purge()
        cleanup_blinkers()


class NodeStatus(Enum):
    ACTIVE = 'ACTIVE'
    LOST = 'LOST'
