import logging
import os
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
LAST_UPDATE_WARN_MINS = 5


class INFO:
    last_update = "Last update within {} minutes".format(LAST_UPDATE_WARN_MINS)
    tank_level = "Tank level within acceptible range"
    pump_ac_state = "Pump AC is on"


class WARN:
    last_update = "No update within {} minutes!".format(LAST_UPDATE_WARN_MINS)
    tank_level = "Tank level exceeded max safe distance!"
    tank_level_unavail = "Tank level data unavailable"
    pump_ac_state = "Pump AC is off!"
    pump_ac_state_unavail = "Pump AC state data unavailable"
    

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
    return - 5  # FIXME


def set_tank_level(level, ts=None):
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


def set_pump_amperage(amperage, ts=None):
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
    now = datetime.now(pytz.UTC)
    if duration == "hour":
        start = int((now - timedelta(hours=1)).timestamp() * 1000)
        bucket_size = 50
    elif duration == "day":
        start = int((now - timedelta(days=1)).timestamp() * 1000)
        bucket_size = 1000
    elif duration == "week":
        start = int((now - timedelta(days=7)).timestamp() * 1000)
        bucket_size = 5000
    elif duration == "month":
        bucket_size = 15000
        start = int((now - timedelta(days=31)).timestamp() * 1000)
    elif duration == "all":
        start = 0
        bucket_size = 15000
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


def set_pump_ac_state(ac_state, ts=None):
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
            warn.append(WARN.tank_level)
        else:
            info.append(INFO.tank_level)
    except:
        warn.append(WARN.tank_level_unavail)

    try:
        if int(get_pump_ac_state()[1]) == 1:
            info.append(INFO.pump_ac_state)
        else:
            warn.append(WARN.pump_ac_state)
    except:
        warn.append(WARN.pump_ac_state_unavail)

    return {
        "info": sorted(info),
        "warn": sorted(warn),
    }
    
