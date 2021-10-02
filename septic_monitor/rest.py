import logging
import pytz
from fastapi import FastAPI

from septic_monitor import storage

app = FastAPI()

# logging.basicConfig(level=logging.INFO)


@app.get("/api/tank/level/")
async def get_tank_level():
    return storage.get_tank_level()


@app.get("/api/tank/level/{duration}/")
async def get_tank_level_duration(duration):
    return [{"x": l.timestamp, "y": l.value} for l in storage.get_tank_level(duration=duration)]


@app.get("/api/pump/amperage/")
async def get_pump_amperage():
    return storage.get_pump_amperage()


@app.get("/api/pump/amperage/{duration}/")
async def get_pump_amperage_duration(duration):
    return [{"x": l.timestamp, "y": l.value} for l in storage.get_pump_amperage(duration=duration)]


@app.get("/api/lastupdate/")
async def lastupdate():
    return storage.get_last_update()
