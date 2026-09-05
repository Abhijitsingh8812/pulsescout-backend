# services/cache_service.py

import time

CACHE = {}

CACHE_DURATION = 120  # 2 minutes


def get_cache(key):

    if key not in CACHE:
        return None

    data = CACHE[key]

    if time.time() - data["timestamp"] > CACHE_DURATION:
        return None

    return data["value"]


def set_cache(key, value):

    CACHE[key] = {
        "timestamp": time.time(),
        "value": value
    }