# GSA ERM2 MCP Toolkit

A small Python MCP server exposing three tools to Bob and any MCP-compatible client.

## Tools

| Tool | Description |
|---|---|
| `gsa_erm2_current_weather` | Returns live weather for a given location via wttr.in |
| `gsa_erm2_programming_joke` | Fetches a programming joke from JokeAPI |
| `gsa_erm2_unit_converter` | Converts between temperature, length, and weight units (local logic) |

## Running

```bash
uv run --project . mcp run server.py
```

## Dependencies

- `mcp[cli] >= 1.0`
- `httpx >= 0.27`
- Python >= 3.11
