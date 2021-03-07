import itertools
import json
import os
import time

from typing import List, Dict

from strobe.music_player import load_audio_file, play_music, stop_music, PLAYBACK_LATENCY
from strobe.scheduler import register_tasks
from strobe.strobe_node import StrobeNode, NodeID, NodeStatus

MASTER_NODE_ID = 'M'

SLAVE_ACTIVE_STATUS_TIMEOUT = 30  # seconds


class StrobeMaster(StrobeNode):
    nodeID: NodeID = os.getenv('STROBE_NODE_ID', MASTER_NODE_ID)

    subsequences: Dict[NodeID, List[int]] = {}
    slaves: Dict[NodeID, Dict] = {}

    def __init__(self, source_sequence_path, audio_path):
        source_sequence = json.loads(open(source_sequence_path, 'r').read())

        self.compile_sequence(source_sequence)
        load_audio_file(audio_path)

    def compile_sequence(self, source_sequence: List[dict]):

        def offsets_alone(elements):
            return list(map(lambda e: int(e['offset']), elements))

        for ID, events in itertools.groupby(source_sequence, lambda o: o['label']):
            self.subsequences[ID] = offsets_alone(events)

    def register_slave(self, node_id: NodeID, ip: str, details: Dict):
        if node_id not in self.slaves:
            self.slaves[node_id] = {'ip': ip, 'wifi': {}, 'chrony': {}}

        for metric, data in details.items():
            self.slaves[node_id][metric] = data

        self.slaves[node_id]['last_update'] = time.time()
        self.slaves[node_id]['status'] = NodeStatus.ACTIVE.value

    def slave_data(self):
        for node_id, data in self.slaves:
            if (time.time() - data['last_update']) > SLAVE_ACTIVE_STATUS_TIMEOUT:
                data['status'] = NodeStatus.LOST.value

        return self.slaves

    def publish_offsets(self):
        self.sequence = []

        for ID, offsets in self.subsequences:

            if ID in self.slaves.keys():
                print(f"TODO: send {len(offsets)} offsets to {self.slaves[ID]['ip']}")
            else:
                self.sequence.extend(offsets)

    def register_tasks(self, start_time_ms: float):
        super().register_tasks(start_time_ms)
        register_tasks(start_time_ms - PLAYBACK_LATENCY, [0] * 1, play_music)

        for ID, details in self.slaves:
            print(f"TODO: notify {ID} {details['ip']}")

    def stop(self):
        super().stop()
        stop_music()

        for ID, details in self.slaves:
            print(f"TODO: stop {ID} {details['ip']}")
