import itertools
import json
import os
import sys

from datetime import datetime
from typing import List, Dict

from blink import setup_blinkers, cleanup_blinkers, blink
from music_player import load_audio_file, play_music, stop_music, PLAYBACK_LATENCY
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

    def load_audio(self, filename):
        if filename is not None:
            load_audio_file(filename)
        return self

    def publish_offsets(self):
        return self

    def start(self, start_time_ms: float):
        register_tasks(start_time_ms, self.subsequences[nodeID], blink)
        register_tasks(start_time_ms - PLAYBACK_LATENCY, [0] * 1, play_music)
        launch().join()

    def stop(self):
        purge()
        stop_music()


def next_full_minute():
    now = datetime.now()
    next_minute = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute + 1)

    return datetime.timestamp(next_minute) * 1000


sourceSequence = json.loads(open(sys.argv[1], 'r').read())
audioFile = sys.argv[2] if len(sys.argv) >= 3 else None

master = Master() \
    .register_slaves() \
    .compile_sequence(sourceSequence) \
    .load_audio(audioFile) \
    .publish_offsets()

try:
    master.start(next_full_minute())
finally:
    try:
        master.stop()
    finally:
        cleanup_blinkers()
