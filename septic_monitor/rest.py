from fastapi import FastAPI

from septic_monitor import storage

app = FastAPI()


@app.get("/api/distance/")
async def distance():
    return storage.get_distance()


@app.get("/api/lastupdate/")
async def distance():
    return storage.get_last_update()
