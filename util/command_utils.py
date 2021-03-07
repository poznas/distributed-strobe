import subprocess

from typing import List, Pattern, Dict


def execute_and_parse(args: List[str], pattern: Pattern[str], key='param', value='value') -> Dict[str, str]:
    result = subprocess.run(args, stdout=subprocess.PIPE).stdout.decode('utf-8')

    entries = [m.groupdict() for m in pattern.finditer(result)]

    return {e[key].strip(): e[value] for e in entries}
