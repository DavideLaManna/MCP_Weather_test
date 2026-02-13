"""
MCP Weather Server

Exposes weather tools via Model Context Protocol using Open-Meteo API (free, no API key).
Runs as stdio server for MCP client connections.
"""

import json

from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("weather")

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _decode_weather_code(code: int) -> str:
    return WMO_CODES.get(code, f"Unknown ({code})")


def _geocode(city: str) -> dict | None:
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return None
    data = resp.json()
    results = data.get("results") or []
    return results[0] if results else None


@mcp.tool()
def get_weather_by_city(city: str) -> str:
    """
    Get current weather for a city using Open-Meteo API.

    Args:
        city: City name (e.g., Rome, Malta, London)

    Returns:
        Current weather information
    """
    loc = _geocode(city)
    if not loc:
        return json.dumps({"error": f"Could not find location: {city}"})

    lat, lon = loc["latitude"], loc["longitude"]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return json.dumps({"error": "Could not fetch weather data"})

    data = resp.json()
    current = data.get("current", {})
    cond = _decode_weather_code(current.get("weather_code", 0))

    result = {
        "city": loc.get("name", city),
        "temperature_c": current.get("temperature_2m"),
        "humidity_pct": current.get("relative_humidity_2m"),
        "wind_kmh": current.get("wind_speed_10m"),
        "conditions": cond,
    }
    return json.dumps(result, indent=2)


@mcp.tool()
def get_forecast_by_city(city: str, days: int = 7) -> str:
    """
    Get weather forecast for a city for the next N days.

    Args:
        city: City name
        days: Number of days (1-7), default 7

    Returns:
        Multi-day forecast information
    """
    loc = _geocode(city)
    if not loc:
        return json.dumps({"error": f"Could not find location: {city}"})

    lat, lon = loc["latitude"], loc["longitude"]
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "forecast_days": min(max(days, 1), 7),
        "timezone": "auto",
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        return json.dumps({"error": "Could not fetch forecast data"})

    data = resp.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    temps_max = daily.get("temperature_2m_max", [])
    temps_min = daily.get("temperature_2m_min", [])
    codes = daily.get("weather_code", [])

    forecast = []
    for i in range(len(dates)):
        forecast.append({
            "date": dates[i],
            "temp_max_c": temps_max[i] if i < len(temps_max) else None,
            "temp_min_c": temps_min[i] if i < len(temps_min) else None,
            "conditions": _decode_weather_code(codes[i] if i < len(codes) else 0),
        })

    result = {"city": loc.get("name", city), "forecast": forecast}
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
