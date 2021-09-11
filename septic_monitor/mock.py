import logging
import random
import time
from datetime import datetime, timedelta

from septic_monitor import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    #now = datetime.now()
    #dist_poll_int = storage.get_dist_poll_int()
    #start = now - timedelta(days=365)
    #logger.info("Creating back-data...")
    #timestamp = start + timedelta(minutes=dist_poll_int)
    # while timestamp  < now:
    #    distance = random.choice(range(20, 40))
    #    storage.set_distance(distance, ts=timestamp)
    #    timestamp = timestamp + timedelta(minutes=dist_poll_int)
    # logger.info("Back-data created!")
    while True:
        distance = random.choice(range(20, 40))
        storage.set_level(distance)
        # time.sleep(dist_poll_int * 60)
        time.sleep(15)


if __name__ == "__main__":
    main()
