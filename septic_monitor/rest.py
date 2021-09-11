import logging
import pytz
from fastapi import FastAPI

from septic_monitor import storage

app = FastAPI()

logging.basicConfig(level=logging.INFO)

@app.get("/api/level/")
async def get_level():
    return storage.get_level()


@app.get("/api/level/{duration}/")
async def get_level(duration):    
    return [        
        {"x": l.timestamp, "y": l.value} for d in storage.get_level(duration=duration)
    ]


@app.get("/api/lastupdate/")
async def lastupdate():    
    return storage.get_last_update()
