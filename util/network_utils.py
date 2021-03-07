import re
import socket

from typing import Dict, Pattern

from util.command_utils import execute_and_parse


# noinspection PyBroadException
# author: fatal_error
def host_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


iwconfig_pattern: Pattern[str] = re.compile(
    r"(?P<param>[\w\-]+( \w+)*)([:=])( )?(?P<value>[\w\d/\-.:\"]+( [\w\d/\-.:\"]+)*)([\n\t]|\s{2,})"
)


def wifi_details(interface='wlan0') -> Dict[str, str]:
    return execute_and_parse(["/sbin/iwconfig", interface], iwconfig_pattern)
