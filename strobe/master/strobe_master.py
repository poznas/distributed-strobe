import itertools
import json
import os
import sys

from datetime import datetime
from typing import List, Dict

from strobe.music_player import load_audio_file, play_music, stop_music, PLAYBACK_LATENCY
from strobe.scheduler import register_tasks
from strobe.strobe_node import StrobeNode, NodeID

MASTER_NODE_ID = 'M'


class StrobeMaster(StrobeNode):
    nodeID: NodeID = os.getenv('STROBE_NODE_ID', MASTER_NODE_ID)

    subsequences: Dict[NodeID, List[int]] = {}
    slave_ips: Dict[NodeID, str] = {}

    def __init__(self, source_sequence_path, audio_path):
        source_sequence = json.loads(open(source_sequence_path, 'r').read())

        self.compile_sequence(source_sequence)
        load_audio_file(audio_path)

    def compile_sequence(self, source_sequence: List[dict]):

        def offsets_alone(elements):
            return list(map(lambda e: int(e['offset']), elements))

        for ID, events in itertools.groupby(source_sequence, lambda o: o['label']):
            self.subsequences[ID] = offsets_alone(events)

    def register_slave(self, node_id: NodeID, ip: str):
        self.slave_ips[node_id] = ip

    def publish_offsets(self):
        self.sequence = []

        for ID, offsets in self.subsequences:

            if ID in self.slave_ips.keys():
                print(f"TODO: send {len(offsets)} offsets to {self.slave_ips[ID]}")
            else:
                self.sequence.extend(offsets)

    def register_tasks(self, start_time_ms: float):
        super().register_tasks(start_time_ms)
        register_tasks(start_time_ms - PLAYBACK_LATENCY, [0] * 1, play_music)

        for ID, IP in self.slave_ips:
            print(f"TODO: notify {ID} {IP}")

    def stop(self):
        super().stop()
        stop_music()

        for ID, IP in self.slave_ips:
            print(f"TODO: stop {ID} {IP}")


def next_full_minute():
    now = datetime.now()
    next_minute = datetime(year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute + 1)

    return datetime.timestamp(next_minute) * 1000


if __name__ == '__main__':

    master = StrobeMaster(sys.argv[1], sys.argv[2])

    master.register_tasks(next_full_minute())

    try:
        master.start()
    finally:
        master.stop()
