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
    tank_level = "tank:level"
    tank_level_poll = "tank:level:poll"
    tank_level_warn = "tank:level:warn"
    pump_amperage = "pump:amperage"
    pump_amperage_warn = "pump:amperage:warn"
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
TANK_LEVEL_POLL = (
    int(REDIS.get(Keys.tank_level_poll)) if REDIS.exists(Keys.tank_level_poll) else 10
)
LEVEL_MAX = (
    int(REDIS.get(Keys.tank_level_warn)) if REDIS.exists(Keys.tank_level_warn) else None
)


def create_rts(key, retention):
    try:
        RTS.create(key, retention=retention, duplicate_policy="last")
    except Exception as e:
        if "key already exists" not in str(e).casefold():
            raise


for rts in (
    (Keys.tank_level, RETENTION_DAYS * MS_IN_DAY),
    (Keys.pump_amperage, RETENTION_DAYS * MS_IN_DAY),
):
    create_rts(rts[0], rts[1])


@attrs
class TankLevel:
    timestamp = attrib()
    value = attrib()


@attrs
class PumpAmperage:
    timestamp = attrib()
    value = attrib()


def get_retention():
    return RETENTION_DAYS


def set_retention(days):
    REDIS.set(Keys.ret_days, days)


def get_tank_level_poll():
    return TANK_LEVEL_POLL


def set_tank_level_poll(minutes):
    REDIS.set(Keys.tank_level_poll, minutes)


def get_tank_level_warn():
    return -5  # FIXME


def set_tank_level(level, ts=None):
    """
    Sets the water level in the db (sensor is zero)
    """
    level = float(0 - abs(level))
    RTS.add(
        Keys.tank_level,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        level,
    )
    logger.info("%s Set level: %s cm", datetime.now(), level)


def get_tank_level(duration=None):
    """
    Gets the latest level, or a duration of levels (from now)
    """
    if not RTS.get(Keys.tank_level):
        logger.error("No tank level data in database!")
        return
    if duration is None:
        ts, v = RTS.get(Keys.tank_level)
        return TankLevel(datetime.fromtimestamp(ts), round(v, 2))
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
        TankLevel(datetime.fromtimestamp(ts), v)
        for ts, v in RTS.range(
            Keys.tank_level,
            start,
            "+",
            aggregation_type="max",
            bucket_size_msec=bucket_size,
        )
    ]


def get_lowest_tank_level():
    return min(l.value for l in get_tank_level(duration="all"))


def set_pump_amperage(amperage, ts=None):
    """
    Sets the pump amperage in the db
    """
    amperage = float(amperage)
    RTS.add(
        Keys.pump_amperage,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        amperage,
    )
    logger.info("%s Set amperage: %s", datetime.now(), amperage)


def get_pump_amperage(duration=None):
    """
    Gets the latest pump amperage, or a duration of amperages (from now)
    """
    if not RTS.get(Keys.pump_amperage):
        logger.error("No pump amperage in database!")
        return
    if duration is None:
        ts, v = RTS.get(Keys.pump_amperage)
        return PumpAmperage(datetime.fromtimestamp(ts), round(v, 2))
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
    return [
        PumpAmperage(datetime.fromtimestamp(ts), v)
        for ts, v in RTS.range(
            Keys.pump_amperage,
            start,
            "+",
            aggregation_type="max",
            bucket_size_msec=bucket_size,
        )
    ]


def set_pump_ac_fail(ts=None):
    """
    Sets a pump AC failure event
    """
    RTS.add(
        Keys.pump_ac_fail,
        int(ts.timestamp()) if ts else int(datetime.now(pytz.UTC).timestamp()),
        1,
    )
    logger.info("%s Pump AC failed", datetime.now())


def get_last_update():
    return max(
        x.timestamp
        for x in (
            get_tank_level(),
            get_pump_amperage(),
        )
    )
