import os
import logging
from datetime import datetime

from attr import attrs, attrib
from redis import Redis
from redistimeseries.client import Client

logger = logging.getLogger(__name__)

REDIS = Redis()
RTS = Client()


class Keys:
    ret_days = "ret_days"
    dist_poll_int = "dist_poll_int"
    min_dist = "min_dist"
    dist = "dist"

# defaults
MS_IN_DAY = 86400000 
RETENTION_DAYS = int(REDIS.get(Keys.ret_days)) if REDIS.exists(Keys.ret_days) else 365
DIST_POLL_INT = int(REDIS.get(Keys.dist_poll_int)) if REDIS.exists(Keys.dist_poll_int) else 10
MIN_DIST = int(REDIS.get(Keys.min_dist)) if REDIS.exists(Keys.min_dist) else None


try:
    RTS.create(Keys.dist, retention_msecs=RETENTION_DAYS*MS_IN_DAY)
except Exception as e:
    if "key already exists" not in str(e):
        logger.error("Something went wrong: %s", e)
        raise


@attrs
class Distance:
    timestamp = attrib()
    value = attrib()


# FIXME - need to handle lost connection

def get_retention():
    return RETENTION_DAYS


def set_retention(days):
    REDIS.set(Keys.ret_days, days)


def get_dist_poll_int():
    return DIST_POLL_INT    


def set_dist_poll_int(minutes):
    REDIS.set(Keys.dist_poll_int, minutes)


def set_distance(distance):
    """
    Sets the distance in the db at the current time
    """
    RTS.add(Keys.dist, int(datetime.now().timestamp()), float(distance))
    logger.info("Set distance: %s cm", distance)


def get_distance():
    """
    Gets the lastest distance from the db
    """
    l = RTS.get(Keys.dist)
    return Distance(datetime.fromtimestamp(l[0]), l[1])
