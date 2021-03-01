import os

from typing import List

from strobe_node import StrobeNode, NodeID
from util.network_utils import host_ip


class StrobeSlave(StrobeNode):

    @staticmethod
    def slave_id() -> NodeID:
        return os.getenv('STROBE_NODE_ID', host_ip()[-1])

    def set_sequence(self, sequence: List[int]):
        self.stop()
        self.sequence = sequence
