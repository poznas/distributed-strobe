import itertools
import json
import os
import sys

from datetime import datetime
from typing import List, Dict

from music_player import load_audio_file, play_music, stop_music, PLAYBACK_LATENCY
from scheduler import register_tasks
from strobe.strobe_node import StrobeNode, NodeID

MASTER_NODE_ID = 'M'

nodeID: NodeID = os.getenv('STROBE_NODE_ID', MASTER_NODE_ID)


class Master(StrobeNode):
    subsequences: Dict[NodeID, List[int]] = {}
    slaves: Dict[NodeID, str] = {}

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

        self.sequence = self.subsequences[nodeID]

        return self

    def load_audio(self, filename):
        if filename is not None:
            load_audio_file(filename)
        return self

    def publish_offsets(self):
        return self

    def register_tasks(self, start_time_ms: float):
        super().register_tasks(start_time_ms)
        register_tasks(start_time_ms - PLAYBACK_LATENCY, [0] * 1, play_music)
        return self

    def stop(self):
        super().stop()
        stop_music()


def next_full_minute():
    now = datetime.now()
    next_minute = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute + 1)

    return datetime.timestamp(next_minute) * 1000


if __name__ == '__main__':
    sourceSequence = json.loads(open(sys.argv[1], 'r').read())
    audioFile = sys.argv[2] if len(sys.argv) >= 3 else None

    master = Master() \
        .register_slaves() \
        .compile_sequence(sourceSequence) \
        .load_audio(audioFile) \
        .publish_offsets() \
        .register_tasks(next_full_minute())

    try:
        master.start()
    finally:
        master.stop()
