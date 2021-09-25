import itertools
import logging
import random
import sys
import time
from datetime import datetime, timedelta

import numpy as np
from scipy import signal

from septic_monitor import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_level():
    t = np.linspace(0, 1, 5000)
    w = signal.sawtooth(2 * np.pi * 5 * t)
    for v in w.tolist():
        dither = random.randrange(-100, 100) / 100.0
        yield -20 + (v * 10) + dither


def back_data():
    now = datetime.now()
    level_poll_int = storage.get_level_poll_int()
    start = now - timedelta(days=60)
    logger.info("Creating back-data...")
    timestamp = start + timedelta(minutes=level_poll_int)
    for level in itertools.cycle(check_level()):
        storage.set_level(level, ts=timestamp)
        if timestamp < now:
            timestamp = timestamp + timedelta(minutes=5)
        else:
            timestamp = datetime.now()
            time.sleep(level_poll_int * 60)


def main():
    if "backdata" in sys.argv:
        back_data()

    while True:
        level = random.choice(range(20, 40))
        storage.set_level(level)
        time.sleep(15)


if __name__ == "__main__":
    main()
