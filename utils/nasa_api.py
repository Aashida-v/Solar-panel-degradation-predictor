# utils/nasa_api.py

import requests

NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"

def get_nasa_data(lat, lon):
    """
    Fetches annual average GHI, temperature, and calculates peak sunlight hours
    from NASA POWER API for the given coordinates.

    Parameters:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        dict: {
            'ghi': float,               # kWh/m²/day
            'temperature': float,      # °C
            'sunlight_hours': float    # hours/day (approx.)
        }
        or None if error occurs
    """
    params = {
        "parameters": "T2M,ALLSKY_SFC_SW_DWN",  # Correct GHI parameter
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON"
    }

    try:
        response = requests.get(NASA_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        ghi_data = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        temp_data = data["properties"]["parameter"]["T2M"]

        ghi_avg = ghi_data["ANN"]
        temp_avg = temp_data["ANN"]

        # Estimate peak sunlight hours (GHI ≈ sunlight hours for average efficiency)
        sunlight_hours = ghi_avg  # already in kWh/m²/day

        return {
            "ghi": round(ghi_avg, 2),
            "temperature": round(temp_avg, 2),
            "sunlight_hours": round(sunlight_hours, 2)
        }

    except Exception as e:
        print("❌ NASA API Error:", e)
        return None