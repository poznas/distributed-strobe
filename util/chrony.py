import re

from typing import Dict

from util.command_utils import execute_and_parse

pattern = re.compile(r"(?P<param>.+): (?P<value>.+)\n")


def chronyc_tracking() -> Dict[str, str]:
    return execute_and_parse(['chronyc', 'tracking'], pattern)
