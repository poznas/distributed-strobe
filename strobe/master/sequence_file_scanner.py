import re
from pathlib import Path
from typing import List


file_name_pattern = re.compile(r"([^/]+)\.\w+$")


def scan_available_sequences(sequence_dir: str) -> List[str]:
    result: List[str] = []

    for file_path in Path(sequence_dir).glob("*.json"):
        name = file_name_pattern.search(file_path.name).group(1)

        # assert audio file exists
        Path(f"{sequence_dir}/{name}.ogg").resolve(strict=True)

        result.append(name)

    if len(result) == 0:
        raise RuntimeError(f"no sequences found in {sequence_dir}")

    return result
