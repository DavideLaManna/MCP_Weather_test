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

No weather API key is needed; Open-Meteo is used.

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

## Tools

| Tool                  | Description                            |
|-----------------------|----------------------------------------|
| `get_weather_by_city` | Current weather for a city             |
| `get_forecast_by_city`| Multi-day forecast (1–7 days)           |

## Troubleshooting

**OPENAI_API_KEY not found** – Add it to `.env`.

**MCP connection errors** – Ensure `server/weather.py` runs correctly on its own.
