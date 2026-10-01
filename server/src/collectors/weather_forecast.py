#!/usr/bin/env python3
"""Return today's local weather forecast as a single readable string."""

from __future__ import annotations

import os
import sys
from dotenv import load_dotenv
from datetime import datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

load_dotenv()

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 15


def get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    request = Request(f"{url}?{urlencode(params)}", headers={"User-Agent": "daily-weather-script/1.0"})
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            import json

            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Weather service returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach the weather service: {exc.reason}") from exc


def geocode(location: str, country_code: str | None = None) -> dict[str, Any]:
    # Util function for getting latitude, longitude, etc. not currently used
    params: dict[str, Any] = {"name": location, "count": 1, "language": "en", "format": "json"}
    if country_code:
        params["countryCode"] = country_code.upper()
    results = get_json(GEOCODING_URL, params).get("results", [])
    if not results:
        raise RuntimeError(f"No location found for {location!r}.")
    return results[0]


def fetch_forecast(latitude: float, longitude: float, time_zone: str, temperature_unit: str) -> dict[str, Any]:

    return get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min",
            "hourly": "precipitation_probability",
            "temperature_unit": temperature_unit,
            "timezone": time_zone,
            "forecast_days": 1,
        },
    )


def format_hour(value: datetime) -> str:
    return value.strftime("%I %p").lstrip("0")


def rain_windows(times: list[str], probabilities: list[int | float | None]) -> list[tuple[datetime, datetime, int]]:
    rainy = [
        (datetime.fromisoformat(time), int(probability))
        for time, probability in zip(times, probabilities)
        if probability is not None and probability > 10
    ]
    if not rainy:
        return []

    windows: list[tuple[datetime, datetime, int]] = []
    start = previous = rainy[0][0]
    peak = rainy[0][1]
    for timestamp, probability in rainy[1:]:
        if (timestamp - previous).total_seconds() > 3600:
            windows.append((start, previous, peak))
            start, peak = timestamp, probability
        else:
            peak = max(peak, probability)
        previous = timestamp
    windows.append((start, previous, peak))
    return windows



def build_forecast_string(data: dict[str, Any]) -> str:
    daily = data["daily"]
    unit = data["daily_units"]["temperature_2m_max"]
    low = round(daily["temperature_2m_min"][0])
    high = round(daily["temperature_2m_max"][0])
    summary = f"Low {low}{unit}, high {high}{unit}."

    windows = rain_windows(data["hourly"]["time"], data["hourly"]["precipitation_probability"])
    if not windows:
        return f"{summary} No rain expected."

    overall_peak = max(window[2] for window in windows)
    descriptions = []
    for start, end, peak in windows:
        # Each hourly value represents that hour, so show the final hour as a one-hour interval.
        end_display = end.replace(hour=(end.hour + 1) % 24)
        descriptions.append(f"{format_hour(start)}-{format_hour(end_display)} (up to {peak}%)")
    return f"{summary} \nChance of rain: {', '.join(descriptions)}."


def get_daily_forecast() -> str:
    latitude = float(os.getenv("LATITUDE").strip())
    longitude = float(os.getenv("LONGITUDE").strip())
    time_zone = os.getenv("TIME_ZONE").strip()

    units = os.getenv("TEMPERATURE_UNIT", "fahrenheit").strip().lower()
    if units not in {"fahrenheit", "celsius"}:
        raise RuntimeError("TEMPERATURE_UNIT must be either fahrenheit or celsius.")
    return build_forecast_string(fetch_forecast(latitude, longitude, time_zone, units))


if __name__ == "__main__":
    try:
        print(get_daily_forecast())
    except (RuntimeError, KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
