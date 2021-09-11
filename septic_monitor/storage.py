import os
import logging
import pytz
import time
import sys
from datetime import datetime, timedelta, timezone

from attr import attrs, attrib
from redis import Redis
from redis.exceptions import ConnectionError
from redistimeseries.client import Client

logger = logging.getLogger(__name__)

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
logger.info(f"Redis host: {REDIS_HOST}")


class Keys:
    ret_days = "ret_days"
    dist_poll_int = "dist_poll_int"
    min_dist = "min_dist"
    dist = "dist"
    dist_hour = "dist:hour"
    amp = "amp"
    

# wait for db
while True:
    try:
        REDIS = Redis(host=REDIS_HOST)
        REDIS.ping()
        RTS = Client(host=REDIS_HOST)
        logger.info("Connected to Redis!")
        break
    except Exception as e:
        logger.error(f"Unable to connect to Redis: {e}")
        time.sleep(5)


MS_IN_DAY = 86400000
MS_IN_HOUR = 3600000
MS_IN_MINUTE = 60000
RETENTION_DAYS = int(REDIS.get(Keys.ret_days)) if REDIS.exists(Keys.ret_days) else 30
DIST_POLL_INT = int(REDIS.get(Keys.dist_poll_int)) if REDIS.exists(Keys.dist_poll_int) else 10
MIN_DIST = int(REDIS.get(Keys.min_dist)) if REDIS.exists(Keys.min_dist) else None


def create_rts(key, retention):
    try:
        RTS.create(key, retention=retention, duplicate_policy="last")
    except Exception as e:
        if "key already exists" not in str(e).casefold():
            raise

for rts in (
        (Keys.dist, RETENTION_DAYS * MS_IN_DAY),
        (Keys.dist_hour, 1 * MS_IN_HOUR),
    ):
        create_rts(rts[0], rts[1])


@attrs
class Distance:
    timestamp = attrib()
    value = attrib()


@attrs
class Amperage:
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


def set_distance(distance, ts=None):
    """
    Sets the distance in the db at the current time
    """
    RTS.add(
        Keys.dist,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        float(distance),
    )
    logger.info("Set distance: %s cm", distance)


def get_distance(duration=None):
    """
    Gets the latest distance, or a duration of distances (from now)
    """
    if duration is None:
        ts, v = RTS.get(Keys.dist)
        return Distance(datetime.fromtimestamp(ts), v)
    now = datetime.now(pytz.UTC)
    if duration == "hour":
        start = int((now - timedelta(hours=1)).timestamp())
        bucket_size = 100
    elif duration == "day":
        start = int((now - timedelta(days=1)).timestamp())
    elif duration == "week":
        start = int((now - timedelta(days=7)).timestamp())
    elif duration == "month":
        start = int((now - timedelta(days=31)).timestamp())
    end = int(now.timestamp())
    return [
        Distance(datetime.fromtimestamp(ts), v) for ts, v in RTS.range(Keys.dist, start, "+", aggregation_type="min", bucket_size_msec=bucket_size)
    ]



def get_amperage():
    """
    Gets the latest amperage fromt he db
    """
    return get_distance()  # FIXME


def get_last_update():    
    return max(
        x.timestamp
        for x in (
            get_distance(),
            get_amperage(),
        )
    )
