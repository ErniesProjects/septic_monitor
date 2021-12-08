import logging
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone

import pytz
from attr import attrib, attrs
from redis import Redis
from redis.exceptions import ConnectionError
from redistimeseries.client import Client

from septic_monitor import logs

logging.basicConfig(level=logging.INFO, format=logs.LOG_FMT)
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
    pump_ac_state = "pump:ac:state"


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


# in milliseconds
SECOND = 1000
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR


RETENTION_DAYS = int(REDIS.get(Keys.ret_days)) if REDIS.exists(Keys.ret_days) else 30
TANK_LEVEL_POLL = (
    int(REDIS.get(Keys.tank_level_poll)) if REDIS.exists(Keys.tank_level_poll) else 10
)
LEVEL_MAX = (
    int(REDIS.get(Keys.tank_level_warn)) if REDIS.exists(Keys.tank_level_warn) else None
)
LAST_UPDATE_WARN_MINS = 5


def create_rts(key, retention):
    try:
        RTS.create(key, retention=retention, duplicate_policy="last")
    except Exception as e:
        if "key already exists" not in str(e).casefold():
            raise


for rts in (
    (Keys.tank_level, RETENTION_DAYS * DAY),
    (Keys.pump_amperage, RETENTION_DAYS * DAY),
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
    return - 5  # FIXME


def set_tank_level(level):
    """
    Sets the water level in the db (sensor is zero)
    """
    level = float(0 - abs(level))
    RTS.add(
        Keys.tank_level,
        "*",
        level,
    )
    logger.info("Set level: %s cm", level)



def duration_to_start_and_bucket(duration):
    now, _ = REDIS.time()
    if duration == "hour":
        start = now - HOUR
        bucket_size = MINUTE
    elif duration == "day":
        start = now - DAY
        bucket_size = 10 * MINUTE
    elif duration == "week":
        start = now - (DAY * 7)
        bucket_size = HOUR
    elif duration == "month":
        start = now - (DAY * 30)
        bucket_size = 6 * HOUR
    elif duration == "all":
        start = 0
        bucket_size = DAY
    return start, bucket_size


def get_tank_level(duration=None):
    """
    Gets the latest level, or a duration of levels (from now)
    """    
    if not RTS.get(Keys.tank_level):
        logger.error("No tank level data in database!")
        return
    if duration is None:
        ts, v = RTS.get(Keys.tank_level)
        return TankLevel(datetime.fromtimestamp(ts/1000.0), round(v, 2))
    start, bucket_size = duration_to_start_and_bucket(duration)
    return [
        TankLevel(datetime.fromtimestamp(ts/1000.0), v)
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


def set_pump_amperage(amperage):
    """
    Sets the pump amperage in the db
    """
    amperage = float(amperage)
    RTS.add(
        Keys.pump_amperage,
        "*",
        amperage,
    )
    logger.info("Set amperage: %s", amperage)


def get_pump_amperage(duration=None):
    """
    Gets the latest pump amperage, or a duration of amperages (from now)
    """
    if not RTS.get(Keys.pump_amperage):
        logger.error("No pump amperage in database!")
        return
    if duration is None:
        ts, v = RTS.get(Keys.pump_amperage)
        return PumpAmperage(datetime.fromtimestamp(ts/1000.0), round(v, 2))
    start, bucket_size = duration_to_start_and_bucket(duration)
    return [
        PumpAmperage(datetime.fromtimestamp(ts/1000.0), v)
        for ts, v in RTS.range(
            Keys.pump_amperage,
            start,
            "+",
            aggregation_type="max",
            bucket_size_msec=bucket_size,
        )
    ]


def set_pump_ac_state(ac_state):
    """
    Sets a pump AC state (0/1)
    """
    RTS.add(
        Keys.pump_ac_state,
        "*",
        ac_state,
    )
    logger.info("Set pump AC state: %s", ac_state)


def get_pump_ac_state():
    return RTS.get(Keys.pump_ac_state)  # FIXME, should return a class


def status():
    info = []
    warn = []

    try:
        tank_level = get_tank_level()
        tank_level_warn = get_tank_level_warn()
        if tank_level.value > tank_level_warn:
            warn.append("Tank Level Exceeded Max!")
        else:
            info.append("Tank Level OK")
    except:
        warn.append("Tank Level Data Unavailable")

    try:
        if int(get_pump_ac_state()[1]) == 1:
            info.append("Pump Power OK")
        else:
            warn.append("Pump Power Loss!")
    except:
        warn.append("Pump Power State Unavailable!")


    total, used, free = shutil.disk_usage(".")
    used_percent = int(used / total * 100)
    if used_percent > 90:
        warn.append("Disk Usage Exceeded 90%!")
    else:
        info.append(f"Disk Usage OK ({used_percent}% used)")

    return {
        "info": sorted(info),
        "warn": sorted(warn),
    }
    
