# utils/geocode.py
import requests

OPENCAGE_BASE = "https://api.opencagedata.com/geocode/v1/json"

def geocode_place(place_name, api_key, limit=1, timeout=8):
    """
    Returns (lat, lon) or None on failure.
    """
    if not place_name:
        return None
    try:
        params = {
            "q": place_name,
            "key": api_key,
            "limit": limit,
            "no_annotations": 1
        }
        r = requests.get(OPENCAGE_BASE, params=params, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if data.get("results"):
            loc = data["results"][0]["geometry"]
            return float(loc["lat"]), float(loc["lng"])
        return None
    except Exception as e:
        print("OpenCage error:", e)
        return None