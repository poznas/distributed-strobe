import os

from datetime import datetime


MIN_EXECUTION_WAIT_TIME = os.getenv('MIN_EXECUTION_WAIT_TIME', 10)


def compute_start_time(seconds_from_now: str, start_at: str) -> float:  # seconds
    now = datetime.now()

    if start_at is not None:
        _time = datetime.strptime(start_at, "%H:%M")
        start_time = datetime(year=now.year, month=now.month, day=now.day, hour=_time.hour, minute=_time.minute)

        if start_time <= now:
            raise ValueError(f"past start time: {start_time}")

        assert_min_wait_time((start_time - now).total_seconds())

        return datetime.timestamp(start_time)

    elif seconds_from_now is not None:
        wait_time = int(seconds_from_now)

        assert_min_wait_time(wait_time)

        return now.timestamp() + wait_time

    else:
        raise ValueError(f"empty params")


def assert_min_wait_time(wait_time):
    if wait_time < MIN_EXECUTION_WAIT_TIME:
        raise ValueError(
            f"the waiting time for the sequence to start should be at least {MIN_EXECUTION_WAIT_TIME}s"
        )
