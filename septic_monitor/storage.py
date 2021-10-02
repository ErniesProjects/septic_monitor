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
    level = "level"
    level_poll = "level:poll"
    level_max = "level:max"
    amperage = "amperage"
    pump_ac_fail = "pump:acFail"


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
LEVEL_POLL_INT = int(REDIS.get(Keys.level_poll)) if REDIS.exists(Keys.level_poll) else 10
LEVEL_MAX = int(REDIS.get(Keys.level_max)) if REDIS.exists(Keys.level_max) else None


def create_rts(key, retention):
    try:
        RTS.create(key, retention=retention, duplicate_policy="last")
    except Exception as e:
        if "key already exists" not in str(e).casefold():
            raise


for rts in (
    (Keys.level, RETENTION_DAYS * MS_IN_DAY),
    (Keys.amperage, RETENTION_DAYS * MS_IN_DAY),
):
    create_rts(rts[0], rts[1])


@attrs
class Level:
    timestamp = attrib()
    value = attrib()


@attrs
class Amperage:
    timestamp = attrib()
    value = attrib()


def get_retention():
    return RETENTION_DAYS


def set_retention(days):
    REDIS.set(Keys.ret_days, days)


def get_level_poll_int():
    return LEVEL_POLL_INT


def set_level_poll_int(minutes):
    REDIS.set(Keys.level_poll, minutes)


def get_max_level():
    return -5  # FIXME


def set_level(level, ts=None):
    """
    Sets the water level in the db (sensor is zero)
    """
    level = float(0 - abs(level))
    RTS.add(
        Keys.level,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        level,
    )
    logger.info("%s Set level: %s cm", datetime.now(), level)


def get_level(duration=None):
    """
    Gets the latest level, or a duration of levels (from now)
    """
    if duration is None:
        ts, v = RTS.get(Keys.level)
        return Level(datetime.fromtimestamp(ts), round(v, 2))
    now = datetime.now(pytz.UTC)
    if duration == "hour":
        start = int((now - timedelta(hours=1)).timestamp())
        bucket_size = 50
    elif duration == "day":
        start = int((now - timedelta(days=1)).timestamp())
        bucket_size = 1000
    elif duration == "week":
        start = int((now - timedelta(days=7)).timestamp())
        bucket_size = 5000
    elif duration == "month":
        bucket_size = 15000
        start = int((now - timedelta(days=31)).timestamp())
    elif duration == "all":
        start = 0
        bucket_size = 15000
    end = int(now.timestamp())
    return [
        Level(datetime.fromtimestamp(ts), v)
        for ts, v in RTS.range(Keys.level, start, "+", aggregation_type="max", bucket_size_msec=bucket_size)
    ]


def get_lowest_level():
    return min(l.value for l in get_level(duration="all"))


def set_amperage(amperage, ts=None):
    """
    Sets the pump amperage in the db
    """
    amperage = float(amperage)
    RTS.add(
        Keys.amperage,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        amperage,
    )
    logger.info("%s Set amperage: %s", datetime.now(), amperage)


def get_amperage(duration=None):
    """
    Gets the latest pump amperage, or a duration of amperages (from now)
    """
    if duration is None:
        ts, v = RTS.get(Keys.amperage)
        return Amperage(datetime.fromtimestamp(ts), round(v, 2))
    now = datetime.now(pytz.UTC)
    if duration == "10min":
        start = int((now - timedelta(minutes=10)).timestamp())
        bucket_size = 1
    elif duration == "hour":
        start = int((now - timedelta(hours=1)).timestamp())
        bucket_size = 50
    elif duration == "day":
        start = int((now - timedelta(days=1)).timestamp())
        bucket_size = 1000
    elif duration == "week":
        start = int((now - timedelta(days=7)).timestamp())
        bucket_size = 5000
    elif duration == "month":
        bucket_size = 15000
        start = int((now - timedelta(days=31)).timestamp())
    elif duration == "all":
        start = 0
        bucket_size = 15000    
    return [
        Amperage(datetime.fromtimestamp(ts), v)
        for ts, v in RTS.range(Keys.amperage, start, "+", aggregation_type="max", bucket_size_msec=bucket_size)
    ]



def set_pump_ac_fail(msg=None, ts=None):
    """
    Sets a pump AC failure event
    """    
    msg = msg or "Pump AC Failed!"
    RTS.add(
        Keys.pump_ac_fail,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        msg,
    )
    logger.info("%s Pump AC failed: %s", datetime.now(), msg)


def get_last_update():
    return max(
        x.timestamp
        for x in (
            get_level(),
            get_amperage(),
        )
    )
