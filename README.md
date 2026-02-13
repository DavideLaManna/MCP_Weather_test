# MCP Weather Chatbot

Demonstrates MCP (Model Context Protocol) server integration with LangChain using the official MCP Python SDK and `langchain-mcp-adapters`. Weather data comes from Open-Meteo (free, no API key).

## Architecture

```
server/weather.py   MCP server (stdio) - get_weather_by_city, get_forecast_by_city
chatbot.py          Interactive chatbot - connects via stdio, uses load_mcp_tools
run_example.py      Single-query example
```

Flow: `StdioServerParameters` -> `stdio_client` -> `ClientSession` -> `load_mcp_tools` -> LangChain agent.

## Setup

```bash
pip install -r requirements.txt
```

Create `.env` with:

```
OPENAI_API_KEY=your_openai_key
```

## Running

**Interactive chatbot:**

```bash
python chatbot.py
```

**Single-query example:**

```bash
python run_example.py
```

**Run MCP server alone** (for debugging):

```bash
python server/weather.py
```

## MCP Inspector UI

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test tools and debug the server.

### Option 1: stdio

1. Install Node.js (for `npx`), then run:

```bash
npx -y @modelcontextprotocol/inspector
```

2. In the Inspector: add a new server, choose **Standard I/O**
3. Set **Command**: `python`
4. Set **Arguments**: `server/weather.py`
5. Set **Working directory** to the project root
6. Connect and use the Tools tab to call `get_weather_by_city` and `get_forecast_by_city`

### Option 2: HTTP

1. Start the server with HTTP transport:

```bash
python server/weather.py --http
```

2. In another terminal, run the Inspector:

```bash
npx -y @modelcontextprotocol/inspector
```

3. Add a server with URL: `http://localhost:8000/mcp`

## Tools

| Tool                     | Description                    |
| ------------------------ | ------------------------------ |
| `get_weather_by_city`  | Current weather for a city     |
| `get_forecast_by_city` | Multi-day forecast (1–7 days) |

## Troubleshooting

**OPENAI_API_KEY not found** – Add it to `.env`.

**MCP connection errors** – Ensure `server/weather.py` runs correctly on its own.
