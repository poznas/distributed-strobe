import sys
import json
import time

from datetime import datetime

import os
from typing import List, Dict

from blink import setup_blinkers, cleanup_blinkers, blink
import itertools

from scheduler import register_tasks, launch, purge

NodeID = str

MASTER_NODE_ID = '1'

nodeID: NodeID = os.getenv('STROBE_NODE_ID', MASTER_NODE_ID)


class Master(object):
    subsequences: Dict[NodeID, List[int]] = {}
    slaves: Dict[NodeID, str] = {}

    def __init__(self):
        setup_blinkers()

    def register_slaves(self):
        return self

    def compile_sequence(self, source_sequence: List[dict]):

        self.subsequences[nodeID] = []

        for slaveID in self.slaves.keys():
            self.subsequences[slaveID] = []

        def offsets_alone(elements):
            return list(map(lambda e: int(e['offset']), elements))

        for ID, events in itertools.groupby(source_sequence, lambda o: o['label']):
            target_node = ID if ID in self.subsequences else nodeID

            self.subsequences[target_node].extend(offsets_alone(events))

        return self

    def publish_offsets(self):
        return self

    def start(self, start_time_ms: float):
        register_tasks(start_time_ms, self.subsequences[nodeID], blink)
        launch().join()

    def stop(self):
        purge()


sourceSequence = json.loads(open(sys.argv[1], 'r').read())

master = Master() \
    .register_slaves() \
    .compile_sequence(sourceSequence) \
    .publish_offsets()

try:
    master.start(time.time() * 1000)
finally:
    try:
        master.stop()
    finally:
        cleanup_blinkers()
