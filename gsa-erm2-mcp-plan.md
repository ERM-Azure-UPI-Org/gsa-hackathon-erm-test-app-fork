# GSA ERM2 MCP Toolkit — Plan

## Top-Level Overview

Build a small Python MCP server (`gsa_erm2_mcp/`) that exposes three tools to Bob and any
other MCP-compatible client. The server uses the `mcp[cli]` SDK (fastmcp decorator style)
and `httpx` for outbound HTTP. Once registered in `.bob/mcp.json`, Bob can call all three
tools natively inside the IDE.

**Goals**
- Prove outbound internet access via a real weather API call.
- Demonstrate a lightweight public API integration (programming jokes).
- Show a pure-local unit-conversion tool with no network dependency.

**Non-goals**
- Authentication / API-key management (all APIs used are public and keyless).
- Multi-file tool splitting (three tools fit cleanly in one `server.py`).
- Deployment outside the local workspace (server runs via `uv run` locally).

---

## Sub-Tasks

---

### Sub-Task 1 — Scaffold the Python package

**Intent**
Create the directory layout and `pyproject.toml` so `uv` can resolve and install
dependencies before any tool code is written.

**Expected Outcomes**
- `gsa_erm2_mcp/` directory exists at the workspace root.
- `gsa_erm2_mcp/pyproject.toml` declares `mcp[cli] >= 1.0` and `httpx >= 0.27` as
  dependencies, with Python ≥ 3.11 constraint.
- `gsa_erm2_mcp/server.py` exists as an empty (or stub) file.
- `gsa_erm2_mcp/README.md` exists with a one-paragraph description.

**Todo List**
- [ ] Create `gsa_erm2_mcp/` directory.
- [ ] Write `gsa_erm2_mcp/pyproject.toml` with package metadata and dependencies.
- [ ] Create empty `gsa_erm2_mcp/server.py`.
- [ ] Create `gsa_erm2_mcp/README.md` with basic usage notes.

**Relevant Context**
- Workspace root: `/home/itzuser/gsa-hackathon-erm-test-app/`
- Existing `.bob/mcp.json` uses `uvx`/`uv` patterns — follow the same toolchain.

**Status** — `[ ] pending`

---

### Sub-Task 2 — Implement `gsa_erm2_current_weather`

**Intent**
Add the first tool to `server.py`. It calls `wttr.in` (no API key required) to return live
weather data, proving that the MCP server has outbound internet access.

**Expected Outcomes**
- `server.py` contains a function `gsa_erm2_current_weather(location: str)` decorated with
  `@mcp.tool()`.
- Calling the tool with a valid city name returns a dict with keys:
  `location`, `temp_c`, `temp_f`, `condition`, `wind_kph`.
- An unreachable API or bad location returns a structured error dict rather than crashing
  the server.

**Todo List**
- [ ] Set up the `FastMCP` app instance and `httpx.AsyncClient` in `server.py`.
- [ ] Implement `gsa_erm2_current_weather` using
  `https://wttr.in/{location}?format=j1`.
- [ ] Parse the JSON response and return the normalised output dict.
- [ ] Add error handling for HTTP failures and unexpected response shapes.

**Relevant Context**
- API: `https://wttr.in/{location}?format=j1` — free, no key, returns JSON.
- Response path for temperature: `current_condition[0].temp_C` / `temp_F`.
- Response path for condition: `current_condition[0].weatherDesc[0].value`.
- Response path for wind: `current_condition[0].windspeedKmph`.

**Status** — `[ ] pending`

---

### Sub-Task 3 — Implement `gsa_erm2_programming_joke`

**Intent**
Add the second tool. It calls the public JokeAPI to fetch a single programming joke,
demonstrating a second outbound API integration with an optional safety filter.

**Expected Outcomes**
- `server.py` contains `gsa_erm2_programming_joke(safe_mode: bool = True)` decorated with
  `@mcp.tool()`.
- Returns `{ "category": "Programming", "joke": "..." }`.
- If `safe_mode=True`, appends `&safe-mode` to the request URL to filter NSFW content.
- Falls back to a hardcoded joke string if the API is unreachable.

**Todo List**
- [ ] Implement `gsa_erm2_programming_joke` using
  `https://v2.jokeapi.dev/joke/Programming?type=single`.
- [ ] Apply `&safe-mode` query param when `safe_mode=True`.
- [ ] Parse `joke` field from the response JSON.
- [ ] Add fallback hardcoded joke for network-failure case.

**Relevant Context**
- API: `https://v2.jokeapi.dev/joke/Programming?type=single` — free, no key.
- Single-type jokes return `{ "joke": "...", "category": "..." }` at the top level.

**Status** — `[ ] pending`

---

### Sub-Task 4 — Implement `gsa_erm2_unit_converter`

**Intent**
Add the third tool using only local arithmetic — no network call. Supports three unit
families: temperature, length, and weight.

**Expected Outcomes**
- `server.py` contains `gsa_erm2_unit_converter(value: float, from_unit: str, to_unit: str)`
  decorated with `@mcp.tool()`.
- Returns `{ "input", "from_unit", "output", "to_unit" }`.
- Supported families and units:
  - **Temperature**: `celsius`, `fahrenheit`, `kelvin`
  - **Length**: `m`, `km`, `ft`, `miles`
  - **Weight**: `kg`, `g`, `lb`, `oz`
- Raises `ValueError` (surfaced as MCP tool error) when units are unknown or from different
  families.

**Todo List**
- [ ] Define unit-family lookup tables and base-unit conversion factors.
- [ ] Implement `gsa_erm2_unit_converter` with normalise-to-base then convert logic.
- [ ] Handle temperature as a special case (offset conversions, not multiplicative).
- [ ] Validate that `from_unit` and `to_unit` belong to the same family.

**Relevant Context**
- Temperature requires formula-based conversion; length and weight use multiplicative
  factors relative to a base unit (`m` and `kg` respectively).

**Status** — `[ ] pending`

---

### Sub-Task 5 — Register server in `.bob/mcp.json`

**Intent**
Make the server available to Bob by adding a `gsa_erm2` entry to the existing MCP config.

**Expected Outcomes**
- `.bob/mcp.json` contains a new `"gsa_erm2"` server entry alongside the existing
  `"watsonx-orchestrate-adk-docs"` entry.
- Entry uses `uv run` so dependency resolution is automatic.
- Bob can discover and call all three `gsa_erm2_*` tools without manual setup.

**Todo List**
- [ ] Add the following entry to `.bob/mcp.json`:
  ```json
  "gsa_erm2": {
    "command": "uv",
    "args": ["run", "--project", "gsa_erm2_mcp", "mcp", "run", "gsa_erm2_mcp/server.py"]
  }
  ```
- [ ] Verify JSON is valid after edit.

**Relevant Context**
- Current `.bob/mcp.json`: `.bob/mcp.json`
- Existing server uses `uvx` + `mcp-proxy`; new server uses `uv run` directly.

**Status** — `[ ] pending`
