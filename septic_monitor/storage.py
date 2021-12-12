import logging
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.errors import DuplicateTable
import pytz
from attr import attrib, attrs

from septic_monitor import logs

logging.basicConfig(level=logging.INFO, format=logs.LOG_FMT)
logger = logging.getLogger(__name__)

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

while True:
    time.sleep(5)
    p = subprocess.run(["pg_isready", "-h", POSTGRES_HOST, "-U", POSTGRES_USER, "-d", POSTGRES_DB], capture_output=True)
    if p.returncode == 0:
        break
    logger.warning("Database not ready...")
    
    

CONN = psycopg2.connect(f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}")



@attrs
class TankLevel:
    timestamp = attrib()
    value = attrib()
    table = "tank_level"


@attrs
class PumpAmperage:
    timestamp = attrib()
    value = attrib()
    table = "pump_amperage"


@attrs
class PumpAcState:
    timestamp = attrib()
    value = attrib()
    table = "pump_ac_state"

        
for data_type in (TankLevel, PumpAmperage, PumpAcState):
    with CONN.cursor() as cursor:
        try:
            cursor.execute(f"CREATE TABLE {data_type.table} (time TIMESTAMPTZ NOT NULL, value DOUBLE PRECISION);")
        except Exception as e:
            if not isinstance(e, DuplicateTable):
                print(e)
        CONN.commit()
    with CONN.cursor() as cursor:
        try:        
            cursor.execute(f"SELECT create_hypertable('data_type.table', 'time');")
            CONN.commit()
        except Exception as e:
            if not isinstance(e, DuplicateTable):
                print(e)    
        CONN.commit()


BUCKETS = {
    "hour": "2 minutes",
    "day": "20 minutes",
    "week": "1 hours",
    "month": "1 hours",
}


def duration_to_args(duration):
    hours = 1 if duration == "hour" else 0
    days = 1 if duration == "day" else 0
    weeks = 1 if duration == "week" else 0
    weeks = 4 if duration == "month" else 0
    return hours, days, weeks


def get_ts_data(data_type, duration=None):
    if not duration:
        with CONN.cursor() as cursor:
            cursor.execute(f"SELECT (time, value) FROM {data_type.table} ORDER BY time DESC LIMIT 1")
            for row in cursor.fetchall():
                return PumpAmperage(row[0], row[1])
    hours, days, weeks = duration_to_args(duration)
    start = datetime.now(pytz.UTC) - timedelta(hours=hours, days=days, weeks=weeks)
    with CONN.cursor() as cursor:
        cursor.execute(
            f"SELECT time_bucket(%s, time) AS bucket, max(value) FROM {data_type.table} WHERE time > %s GROUP BY bucket ORDER BY bucket ASC",
            (BUCKETS[duration], start)
        )        
        return [data_type(row[0], row[1]) for row in cursor.fetchall()]


def set_ts_data(data_type, value):    
    with CONN.cursor() as cursor:
        cursor.execute(f"INSERT INTO {data_type.table} (time, value) VALUES (now(), %s)", (value,))
    CONN.commit()


def set_tank_level(level):
    level = 0 - abs(level)
    set_ts_data(TankLevel, level)
    logger.info("Set tank level: %s", level)


def get_tank_level(duration=None):
    return get_ts_data(TankLevel, duration=duration)
    

def set_pump_amperage(amperage):
    set_ts_data(PumpAmperage, amperage)
    logger.info("Set amperage: %s", amperage)


def get_pump_amperage(duration=None):
    return get_ts_data(PumpAmperage, duration=duration)
    

def set_pump_ac_state(state):
    set_ts_data(PumpAcState, state)
    logger.info("Set pump AC state: %s", state)


def get_pump_ac_state():
    return get_ts_data(PumpAcState, duration=None)    



def status(short=False):
    info = []
    warn = []

    try:
        tank_level = get_tank_level()
        tank_level_warn = get_tank_level_warn()
        if tank_level.value > tank_level_warn:
            msg = "LVL WARN!" if short else "Tank Level Exceeded Max!" 
            warn.append(msg)
        else:
            msg = "LVL OK" if short else "Tank Level OK"
            info.append(msg)
    except:
        msg = "LVL?" if short else "Tank Level Data Unavailable"
        warn.append(msg)

    try:
        if int(get_pump_ac_state()[1]) == 1:
            msg = "PWR OK" if short else "Pump Power OK"
            info.append()
        else:
            msg = "PWR LOSS!" if short else "Pump Power Loss!"
            warn.append(msg)
    except:
        msg = "PWR?" if short else "Pump Power State Unavailable!"
        warn.append()


    total, used, free = shutil.disk_usage(".")
    used_percent = int(used / total * 100)
    if used_percent > 90:
        msg = "HD WARN!" if short else "Disk Usage Exceeded 90%!"
        warn.append()
    else:
        msg = "HD OK" if short else f"Disk Usage OK ({used_percent}% used)"
        info.append()

    return {
        "info": sorted(info),
        "warn": sorted(warn),
    }
