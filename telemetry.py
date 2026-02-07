import os
import fastf1
import pandas as pd

cache_dir = "/tmp/fastf1_cache"
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)


def get_telemetry(year, track, session_type, driver_code):
    session = fastf1.get_session(year, track, session_type)
    session.load()

    lap = session.laps.pick_driver(driver_code).pick_fastest()
    tel = lap.get_telemetry()

    return tel[['Distance', 'Speed', 'Throttle', 'Brake', 'X', 'Y']]
