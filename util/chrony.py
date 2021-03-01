import re
import subprocess

from typing import Dict

pattern = re.compile(r"(?P<param>.+): (?P<value>.+)\n")


def chronyc_tracking() -> Dict[str, str]:
    result = subprocess.run(['chronyc', 'tracking'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    entries = [m.groupdict() for m in pattern.finditer(result)]

    return {e['param'].strip(): e['value'] for e in entries}
