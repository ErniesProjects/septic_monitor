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


def back_data():
    t = datetime.now()
    for i in range(60):
        t = t - timedelta(days=i)
        storage.set_tank_level(40 - (4 * t.weekday()))


def main():
    if "backdata" in sys.argv:
        back_data()

    while True:
        storage.set_tank_level(40 - (4 * datetime.now().weekday()))
        storage.set_pump_amperage(random.choice(
            [0,] * 30 + [random.choice(range(11, 13)),]
        ))
        time.sleep(60)


if __name__ == "__main__":
    main()
