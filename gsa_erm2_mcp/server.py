"""
GSA ERM2 MCP Toolkit
Exposes three tools:
  - gsa_erm2_current_weather   : live weather via wttr.in
  - gsa_erm2_programming_joke  : programming joke via JokeAPI
  - gsa_erm2_unit_converter    : local unit conversion (temperature, length, weight)
"""

from __future__ import annotations

import httpx
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("gsa_erm2")

# ---------------------------------------------------------------------------
# Tool 1 — current weather
# ---------------------------------------------------------------------------

@mcp.tool()
async def gsa_erm2_current_weather(location: str) -> dict:
    """Return live weather for a given city or lat/lon via wttr.in (no API key needed).

    Args:
        location: City name (e.g. "Washington DC") or "lat,lon" string.

    Returns:
        dict with keys: location, temp_c, temp_f, condition, wind_kph.
        On failure returns dict with key "error".
    """
    url = f"https://wttr.in/{location}?format=j1"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers={"User-Agent": "gsa-erm2-mcp/0.1"})
            resp.raise_for_status()
            data = resp.json()
        current = data["current_condition"][0]
        return {
            "location": location,
            "temp_c": float(current["temp_C"]),
            "temp_f": float(current["temp_F"]),
            "condition": current["weatherDesc"][0]["value"],
            "wind_kph": float(current["windspeedKmph"]),
        }
    except httpx.HTTPStatusError as exc:
        return {"error": f"HTTP {exc.response.status_code} from wttr.in"}
    except httpx.RequestError as exc:
        return {"error": f"Network error: {exc}"}
    except (KeyError, IndexError, ValueError) as exc:
        return {"error": f"Unexpected response shape: {exc}"}


# ---------------------------------------------------------------------------
# Tool 2 — programming joke
# ---------------------------------------------------------------------------

_FALLBACK_JOKE = (
    "Why do programmers prefer dark mode? "
    "Because light attracts bugs!"
)


@mcp.tool()
async def gsa_erm2_programming_joke(safe_mode: bool = True) -> dict:
    """Fetch a single programming joke from JokeAPI.

    Args:
        safe_mode: When True (default), only family-friendly jokes are returned.

    Returns:
        dict with keys: category, joke.
        Falls back to a hardcoded joke if the API is unreachable.
    """
    url = "https://v2.jokeapi.dev/joke/Programming?type=single"
    if safe_mode:
        url += "&safe-mode"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        return {
            "category": data.get("category", "Programming"),
            "joke": data["joke"],
        }
    except Exception:
        return {
            "category": "Programming",
            "joke": _FALLBACK_JOKE,
        }


# ---------------------------------------------------------------------------
# Tool 3 — unit converter (local logic, no network)
# ---------------------------------------------------------------------------

# Length: base unit = metres
_LENGTH_TO_M: dict[str, float] = {
    "m": 1.0,
    "km": 1_000.0,
    "ft": 0.3048,
    "miles": 1_609.344,
}

# Weight: base unit = kilograms
_WEIGHT_TO_KG: dict[str, float] = {
    "kg": 1.0,
    "g": 0.001,
    "lb": 0.45359237,
    "oz": 0.02834952,
}

_TEMPERATURE_UNITS = {"celsius", "fahrenheit", "kelvin"}


def _temp_to_celsius(value: float, from_unit: str) -> float:
    if from_unit == "celsius":
        return value
    if from_unit == "fahrenheit":
        return (value - 32) * 5 / 9
    if from_unit == "kelvin":
        return value - 273.15
    raise ValueError(f"Unknown temperature unit: {from_unit}")


def _celsius_to(value: float, to_unit: str) -> float:
    if to_unit == "celsius":
        return value
    if to_unit == "fahrenheit":
        return value * 9 / 5 + 32
    if to_unit == "kelvin":
        return value + 273.15
    raise ValueError(f"Unknown temperature unit: {to_unit}")


@mcp.tool()
def gsa_erm2_unit_converter(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert a value between units within the same family.

    Supported families:
      - Temperature: celsius, fahrenheit, kelvin
      - Length:      m, km, ft, miles
      - Weight:      kg, g, lb, oz

    Args:
        value:     Numeric value to convert.
        from_unit: Source unit (case-insensitive).
        to_unit:   Target unit (case-insensitive).

    Returns:
        dict with keys: input, from_unit, output, to_unit.

    Raises:
        ValueError: Unknown unit or cross-family conversion attempted.
    """
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    # Determine family
    if from_unit in _TEMPERATURE_UNITS and to_unit in _TEMPERATURE_UNITS:
        celsius = _temp_to_celsius(value, from_unit)
        result = _celsius_to(celsius, to_unit)
    elif from_unit in _LENGTH_TO_M and to_unit in _LENGTH_TO_M:
        base = value * _LENGTH_TO_M[from_unit]
        result = base / _LENGTH_TO_M[to_unit]
    elif from_unit in _WEIGHT_TO_KG and to_unit in _WEIGHT_TO_KG:
        base = value * _WEIGHT_TO_KG[from_unit]
        result = base / _WEIGHT_TO_KG[to_unit]
    else:
        # Diagnose the problem for a useful error message
        all_units = (
            _TEMPERATURE_UNITS
            | set(_LENGTH_TO_M)
            | set(_WEIGHT_TO_KG)
        )
        unknown = [u for u in (from_unit, to_unit) if u not in all_units]
        if unknown:
            raise ValueError(f"Unknown unit(s): {unknown}")
        raise ValueError(
            f"Units '{from_unit}' and '{to_unit}' belong to different families."
        )

    return {
        "input": value,
        "from_unit": from_unit,
        "output": round(result, 6),
        "to_unit": to_unit,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
