import logging
import random
import time

from septic_monitor import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():    
    logger.info("Storage Retention: %d days", storage.get_retention())
    while True:
        distance = random.choice(range(20, 40))
        storage.set_distance(distance)
        time.sleep(10)


if __name__ == "__main__":
    main()        
