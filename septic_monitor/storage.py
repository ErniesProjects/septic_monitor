import logging
from datetime import datetime

from attr import attrs, attrib
from redistimeseries.client import Client

logger = logging.getLogger(__name__)

RTS = Client()

try:
    RTS.create("distance")
except Exception as e:
    if "key already exists" not in str(e):
        logger.error("Something went wrong: %s", e)
        raise


@attrs
class Distance:
    timestamp = attrib()
    value = attrib()


def set_distance(distance):
    """
    Sets the distance in the db at the current time
    """
    RTS.add("distance", int(datetime.now().timestamp()), float(distance))
    logger.info("Added distance: %s", distance)


def get_distance():
    """
    Gets the lastest distance from the db
    """
    l = RTS.get("distance")
    return Distance(datetime.fromtimestamp(l[0]), l[1])
