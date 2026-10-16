
import requests

API_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes
WEATHER_CODES = {
    0: "Clear",
    1: "Mostly sunny",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Scattered showers",
    81: "Rain showers",
    82: "Heavy rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorms",
    96: "Thunderstorms with hail",
    99: "Severe thunderstorms with hail",
}


def get_weather_summary(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
        "forecast_days": 1,
    }

    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()
    daily = response.json()["daily"]

    def value(key):
        result = daily[key][0]
        return None if result is None else result

    high = value("temperature_2m_max")
    low = value("temperature_2m_min")
    code = value("weather_code")
    rain_chance = value("precipitation_probability_max")
    precip = value("precipitation_sum")
    wind = value("wind_speed_10m_max")
    date = daily["time"][0]

    condition = WEATHER_CODES.get(code, "Mixed conditions")

    parts = [
        f"{condition} today",
        f"high of {high:.0f}-F and low of {low:.0f}^F",
    ]

    if rain_chance is not None:
        parts.append(f"{rain_chance:.0f}% chance of precipitation")

    if precip is not None:
        parts.append(f"{precip:.2f} in total precipitation")

    if wind is not None:
        parts.append(f"winds up to {wind:.0f} mph")

    return "; ".join(parts) + "."


if __name__ == "__main__":
    # Example coordinates: Boston, Massachusetts
    print(get_weather_summary(42.3601, -71.0589))
