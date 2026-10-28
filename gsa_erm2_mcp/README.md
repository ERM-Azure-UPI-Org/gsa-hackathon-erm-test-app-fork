# GSA ERM2 MCP Toolkit

A small Python MCP server exposing three tools to Bob and any MCP-compatible client.

## Tools

| Tool | Description |
|---|---|
| `gsa_erm2_current_weather` | Returns live weather for a given location via wttr.in |
| `gsa_erm2_programming_joke` | Fetches a programming joke from JokeAPI |
| `gsa_erm2_unit_converter` | Converts between temperature, length, weight, volume, speed, and time units (local logic) |

### Unit converter families

| Family | Units |
|---|---|
| Temperature | `celsius`, `fahrenheit`, `kelvin` |
| Length | `m`, `km`, `ft`, `miles` |
| Weight | `kg`, `g`, `lb`, `oz` |
| Volume | `l`, `ml`, `gal` (US), `fl_oz` (US) |
| Speed | `m/s`, `km/h`, `mph`, `knots` |
| Time | `s`, `min`, `h`, `d` |

## Running

```bash
uv run --project . mcp run server.py
```

## Testing

```bash
uv run --with "mcp[cli]>=1.0" --with "httpx>=0.27" --with pytest pytest
```

## Dependencies

- `mcp[cli] >= 1.0`
- `httpx >= 0.27`
- Python >= 3.11
