import logging
import random
import sys
import time
from datetime import datetime, timedelta

from septic_monitor import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def back_data():
    now = datetime.now()
    level_poll_int = storage.get_level_poll_int()
    start = now - timedelta(days=365)
    logger.info("Creating back-data...")
    timestamp = start + timedelta(minutes=level_poll_int)
    while timestamp  < now:
       level = random.choice(range(20, 40))
       storage.set_level(level, ts=timestamp)
       timestamp = timestamp + timedelta(minutes=level_poll_int)
    logger.info("Back-data created!")

def main():
    if "backdata" in sys.argv:
        back_data()
        
    while True:
        level = random.choice(range(20, 40))
        storage.set_level(level)        
        time.sleep(15)


if __name__ == "__main__":
    main()
