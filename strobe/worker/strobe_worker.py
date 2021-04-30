import os

from typing import List

from strobe.strobe_node import StrobeNode, NodeID
from util.network_utils import host_ip


class StrobeWorker(StrobeNode):

    @staticmethod
    def worker_id() -> NodeID:
        return os.getenv('STROBE_NODE_ID', host_ip()[-1])

    def set_sequence(self, sequence: List[int]):
        self.stop()
        self._sequence = sequence
