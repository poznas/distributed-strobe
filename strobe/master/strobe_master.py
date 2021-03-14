import copy
import itertools
import json
import os
import time
from typing import List, Dict

import requests
from requests import RequestException

from strobe.master.parse_utils import compute_start_time
from strobe.music_player import load_audio_file, play_music, PLAYBACK_LATENCY, init_mixer, register_countdown
from strobe.strobe_node import StrobeNode, NodeID, NodeStatus
from util.logger import logger

MASTER_NODE_ID = 'M'

SLAVE_PORT = os.getenv('SLAVE_HOST', '5000')
SLAVE_PROTOCOL = os.getenv('SLAVE_PROTOCOL', 'http')
SLAVE_ACTIVE_STATUS_TIMEOUT = 30  # seconds
MIN_EXECUTION_WAIT_TIME = 10  # seconds


class StrobeMaster(StrobeNode):
    nodeID: NodeID = os.getenv('STROBE_NODE_ID', MASTER_NODE_ID)

    _audio_path: str = ""

    subsequences: Dict[NodeID, List[int]] = {}
    _slaves: Dict[NodeID, Dict] = {}

    _active_sequence_meta = {}

    def __init__(self, source_sequence_path, audio_path):
        source_sequence = json.loads(open(source_sequence_path, 'r').read())

        self.compile_sequence(source_sequence)
        self._audio_path = audio_path


    def compile_sequence(self, source_sequence: List[dict]):

        source = copy.deepcopy(source_sequence)
        source.sort(key=lambda o: o['label'])

        def offsets_alone(elements):
            return list(map(lambda e: int(e['offset']), elements))

        for ID, events in itertools.groupby(source, lambda o: o['label']):
            self.subsequences[ID] = offsets_alone(events)


    def register_slave(self, node_id: NodeID, ip: str, details: Dict):
        if node_id not in self.slaves:
            self._slaves[node_id] = {'ip': ip, 'baseURL': f"{SLAVE_PROTOCOL}://{ip}:{SLAVE_PORT}",
                                     'wifi': {}, 'chrony': {}}

        for metric, data in details.items():
            self._slaves[node_id][metric] = data

        self._slaves[node_id]['last_update'] = time.time()
        self._slaves[node_id]['status'] = NodeStatus.ACTIVE.value


    @property
    def slaves(self):
        for node_id, data in self._slaves.items():
            if (time.time() - data['last_update']) > SLAVE_ACTIVE_STATUS_TIMEOUT:
                data['status'] = NodeStatus.LOST.value

        return self._slaves


    def active_slaves_ids(self) -> List[str]:
        return list(filter(lambda s: self.slaves[s]['status'] == NodeStatus.ACTIVE.value, self._slaves.keys()))


    def publish_offsets(self):
        self._sequence = []

        for ID, offsets in self.subsequences.items():

            if ID in self.active_slaves_ids():
                url = f"{self._slaves[ID]['baseURL']}/slave/sequence"
                rs = requests.put(url, json=offsets)
                logger.info(f"PUT {url} [{len(offsets)}] -> {rs.status_code}")
            else:
                logger.warn(f"{ID} is not an active slave, assigning offsets to master")
                self._sequence.extend(offsets)


    def register_execution(self, seconds_from_now: str, start_at: str):

        start_time = compute_start_time(seconds_from_now, start_at)
        start_time_ms = start_time * 1000

        for ID in self.active_slaves_ids():
            url = f"{self._slaves[ID]['baseURL']}/slave/execution?start_time={start_time_ms}"
            try:
                rs = requests.post(url)
                logger.info(f"POST {url} -> {rs.status_code}")
            except RequestException as e:
                logger.error(e)
                self.stop()
                raise e

        self._sequence_scheduler.register_task(0, init_mixer)
        self._sequence_scheduler.register_task(1, lambda: load_audio_file(self._audio_path))

        register_countdown(lambda delay_seconds, fun: self._sequence_scheduler.register_task(
            start_time_ms - PLAYBACK_LATENCY + (delay_seconds * 1000), fun))

        self._sequence_scheduler.register_task(start_time_ms - PLAYBACK_LATENCY, play_music)
        super().register_tasks(start_time_ms)

        self._active_sequence_meta['start_time'] = start_time

    @property
    def active_sequence(self):
        if self._sequence_scheduler.empty():
            self._active_sequence_meta = {}
        return self._active_sequence_meta


    def stop(self):
        super().stop()

        for ID in self.active_slaves_ids():
            url = f"{self._slaves[ID]['baseURL']}/slave/execution"
            try:
                rs = requests.delete(url)
                logger.info(f"DELETE {url} -> {rs.status_code}")
            except RequestException as e:
                logger.error(e)
