import os
import sched
import threading
import time

import requests
from requests import RequestException
from typing import Dict

from strobe.strobe_node import NodeID
from util.chrony import chronyc_tracking
from util.logger import logger
from util.network_utils import wifi_details

MASTER_HOST = os.getenv('STROBE_MASTER_HOST', 'http://192.168.0.110:5000')
SLEEP_PERIOD = 10  # seconds

DETAILS_TO_INCLUDE = {
    'wifi': {
        'interval': 2,  # send wifi details every every nth heartbeat
        'supplier': wifi_details
    },
    'chrony': {
        'interval': 20,  # send chrony details every every nth heartbeat
        'supplier': chronyc_tracking
    }
}


class DetailsProvider:
    counters: Dict[str, int] = {key: 0 for key in DETAILS_TO_INCLUDE.keys()}
    suppliers: Dict[str, callable] = {key: val['supplier'] for key, val in DETAILS_TO_INCLUDE.items()}

    def data(self) -> Dict[str, Dict]:
        result: Dict[str, Dict] = {}

        for name, counter in self.counters.items():
            if counter >= DETAILS_TO_INCLUDE[name]['interval'] - 1:
                self.counters[name] = 0
            else:
                if counter == 0:
                    result[name] = self.suppliers[name]()
                self.counters[name] += 1

        return result


details_provider = DetailsProvider()
s = sched.scheduler(time.time, time.sleep)

node_id: NodeID or None = None


def heartbeat(sc=s):
    s.enter(SLEEP_PERIOD, 1, heartbeat, (sc,))

    url = f"{MASTER_HOST}/master/slaves?node_id={node_id}"

    try:
        details = details_provider.data()
        logger.info(details)
        rs = requests.put(url, json=details)
        logger.info(f"PUT {url} -> {rs.status_code}")

    except RequestException as e:
        logger.error(e)


def start_heartbeat(_node_id: NodeID):
    global node_id

    if node_id is not None:
        return

    node_id = _node_id

    def run_heartbeat():
        os.nice(20)
        s.enter(1, 1, heartbeat, (s,))
        s.run()

    t = threading.Thread(target=run_heartbeat)
    t.start()
