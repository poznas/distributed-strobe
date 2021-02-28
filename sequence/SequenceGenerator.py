#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Converts .srt into array of offsets with labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage: python SequenceGenerator.py tatu.srt
"""
import json
import os
import re
import sys

from typing import Dict

currentDir = os.path.dirname(os.path.realpath(__file__))
defaultTargetFilename = f'{currentDir}/strobe-sequence.json'

source = open(sys.argv[1], 'r').read()
targetFilename = sys.argv[2] if len(sys.argv) >= 3 else defaultTargetFilename
targetFile = open(targetFilename, 'w+')

pattern = re.compile(
    r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+),(?P<milliseconds>\d+) --> \d+:\d+:\d+,\d+\n(?P<caption>[^\n]*)\n"
)


def to_milliseconds(caption: Dict[str, str]) -> str:
    result = int(caption["milliseconds"])
    result += int(caption["seconds"]) * 1000
    result += int(caption["minutes"]) * 1000 * 60
    result += int(caption["hours"]) * 1000 * 60 * 60

    return f"{result}"


captions = [m.groupdict() for m in pattern.finditer(source)]

events = list(map(lambda c: dict(offset=to_milliseconds(c), label=c['caption']), captions))

targetFile.write(json.dumps(events))
targetFile.close()
