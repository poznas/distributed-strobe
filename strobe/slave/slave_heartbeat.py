import os
import sched
import threading
import time

import requests

from strobe.strobe_node import NodeID
from util.logger import logger

s = sched.scheduler(time.time, time.sleep)

SLEEP_PERIOD = 10  # seconds
MASTER_HOST = os.getenv('STROBE_MASTER_HOST', 'http://192.168.0.110:5000')

node_id: NodeID


def heartbeat(sc=s):
    s.enter(SLEEP_PERIOD, 1, heartbeat, (sc,))

    url = f"{MASTER_HOST}/master/slaves?node_id={node_id}"

    try:
        rs = requests.put(url)
        logger.debug(f"PUT {url} -> {rs.status_code}")
    except Exception as e:
        logger.error(e)


def start_heartbeat(_node_id: NodeID):
    global node_id
    node_id = _node_id

    def run_heartbeat():
        os.nice(20)
        s.enter(SLEEP_PERIOD, 1, heartbeat, (s,))
        s.run()

    t = threading.Thread(target=run_heartbeat)
    t.start()
