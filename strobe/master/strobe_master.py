import copy
import itertools
import json
import os
import time
from typing import List, Dict

import requests
from requests import RequestException

from strobe.master.parse_utils import compute_start_time
from strobe.master.sequence_file_scanner import scan_available_sequences
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

    _workers: Dict[NodeID, Dict] = {}

    _sequence_dir: str
    available_sequences: List[str]

    _active_sequence: Dict = {
        # name
        # start_time
    }

    def __init__(self, sequence_dir):
        self._sequence_dir = sequence_dir
        self.available_sequences = scan_available_sequences(sequence_dir)


    def register_worker(self, node_id: NodeID, ip: str, details: Dict):
        if node_id not in self.workers:
            self._workers[node_id] = {'ip': ip, 'baseURL': f"{SLAVE_PROTOCOL}://{ip}:{SLAVE_PORT}",
                                     'wifi': {}, 'chrony': {}}

        for metric, data in details.items():
            self._workers[node_id][metric] = data

        self._workers[node_id]['last_update'] = time.time()
        self._workers[node_id]['status'] = NodeStatus.ACTIVE.value


    @property
    def workers(self):
        for node_id, data in self._workers.items():
            if (time.time() - data['last_update']) > SLAVE_ACTIVE_STATUS_TIMEOUT:
                data['status'] = NodeStatus.LOST.value

        return self._workers


    def active_workers_ids(self) -> List[str]:
        return list(filter(lambda s: self.workers[s]['status'] == NodeStatus.ACTIVE.value, self._workers.keys()))


    def sequence_file(self, extension: str):
        return f"{self._sequence_dir}/{self._active_sequence['name']}.{extension}"


    def compile_sequence(self) -> Dict[NodeID, List[int]]:

        source_sequence = json.loads(open(self.sequence_file('json'), 'r').read())

        source = copy.deepcopy(source_sequence)
        source.sort(key=lambda o: o['label'])

        def offsets_alone(elements):
            return list(map(lambda e: int(e['offset']), elements))

        return {ID: offsets_alone(events) for ID, events in itertools.groupby(source, lambda o: o['label'])}


    def set_active_sequence(self, sequence_name: str):
        self._active_sequence['name'] = sequence_name

        self._sequence = []

        for ID, offsets in self.compile_sequence().items():

            if ID in self.active_workers_ids():
                url = f"{self._workers[ID]['baseURL']}/worker/sequence"
                rs = requests.put(url, json=offsets)
                logger.info(f"PUT {url} [{len(offsets)}] -> {rs.status_code}")
            else:
                logger.warn(f"{ID} is not an active worker, assigning offsets to master")
                self._sequence.extend(offsets)


    @property
    def active_sequence(self):
        if self._sequence_scheduler.empty() and 'start_time' in self._active_sequence:
            del self._active_sequence['start_time']
        return self._active_sequence


    def register_execution(self, seconds_from_now: str, start_at: str):

        start_time = compute_start_time(seconds_from_now, start_at)
        start_time_ms = start_time * 1000

        for ID in self.active_workers_ids():
            url = f"{self._workers[ID]['baseURL']}/worker/execution?start_time={start_time_ms}"
            try:
                rs = requests.post(url)
                logger.info(f"POST {url} -> {rs.status_code}")
            except RequestException as e:
                logger.error(e)
                self.stop()
                raise e

        self._sequence_scheduler.register_task(0, init_mixer)

        audio_file = self.sequence_file('ogg')
        self._sequence_scheduler.register_task(1, lambda: load_audio_file(audio_file))

        register_countdown(lambda delay_seconds, fun: self._sequence_scheduler.register_task(
            start_time_ms - PLAYBACK_LATENCY + (delay_seconds * 1000), fun))

        self._sequence_scheduler.register_task(start_time_ms - PLAYBACK_LATENCY, play_music)
        super().register_tasks(start_time_ms)

        self._active_sequence['start_time'] = start_time


    def stop(self):
        super().stop()

        for ID in self.active_workers_ids():
            url = f"{self._workers[ID]['baseURL']}/worker/execution"
            try:
                rs = requests.delete(url)
                logger.info(f"DELETE {url} -> {rs.status_code}")
            except RequestException as e:
                logger.error(e)
