import logging
import os
import shutil
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
CONN = psycopg2.connect(f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}")



@attrs
class TankLevel:
    timestamp = attrib()
    value = attrib()


@attrs
class PumpAmperage:
    timestamp = attrib()
    value = attrib()
    

CREATE_TABLE = "CREATE TABLE {} (time TIMESTAMPTZ NOT NULL, {} DOUBLE PRECISION);"
CREATE_HYPERTABLE = "SELECT create_hypertable('{}', 'time');"
for table in ("tank_level", "pump_amperage", "pump_ac_state"):    
    with CONN.cursor() as cursor:
        try:
            cursor.execute(CREATE_TABLE.format(table, table.partition("_")[2]))            
        except Exception as e:
            if not isinstance(e, DuplicateTable):
                print(e)
        CONN.commit()
    with CONN.cursor() as cursor:
        try:        
            cursor.execute(CREATE_HYPERTABLE.format(table))
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

def set_tank_level(level):
    level = 0 - abs(level)
    with CONN.cursor() as cursor:
        cursor.execute("INSERT INTO tank_level (time, level) VALUES (now(), %s)", (level,))    
    CONN.commit()
    logger.info("Set tank level: %s", level)

def get_tank_level(duration=None):
    if not duration:
        return TankLevel(datetime.now(), 10.2)  # FIXME
    hours, days, weeks = duration_to_args(duration)
    start = datetime.now(pytz.UTC) - timedelta(hours=hours, days=days, weeks=weeks)
    with CONN.cursor() as cursor:
        cursor.execute(
            "SELECT time_bucket(%s, time) AS bucket, max(level) FROM tank_level WHERE time > %s GROUP BY bucket ORDER BY bucket ASC",            
            (BUCKETS[duration], start)
        )        
        return [TankLevel(row[0], row[1]) for row in cursor.fetchall()]


def set_pump_amperage(amperage):
    with CONN.cursor() as cursor:
        cursor.execute("INSERT INTO pump_amperage (time, amperage) VALUES (now(), %s)", (amperage,))
    CONN.commit()
    logger.info("Set amperage: %s", amperage)


def get_pump_amperage(duration=None):    
    if not duration:
        return PumpAmperage(datetime.now(), 10.2)  # FIXME
    hours, days, weeks = duration_to_args(duration)
    start = datetime.now(pytz.UTC) - timedelta(hours=hours, days=days, weeks=weeks)
    with CONN.cursor() as cursor:
        cursor.execute(
            "SELECT time_bucket(%s, time) AS bucket, max(amperage) FROM pump_amperage WHERE time > %s GROUP BY bucket ORDER BY bucket ASC",
            (BUCKETS[duration], start)
        )        
        return [PumpAmperage(row[0], row[1]) for row in cursor.fetchall()]


def set_pump_ac_state(state):
    #with CONN.cursor() as cursor:
    #    cursor.execute("INSERT INTO pump_amperage (time, amperage) VALUES (now(), %s)", (amperage,))
    logger.info("Set pump AC state: %s", state)


def status():
    return {
        "info": ["foo"],
        "warn": ["bar"]
    }
