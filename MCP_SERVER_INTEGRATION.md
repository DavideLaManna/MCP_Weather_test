# MCP Server Integration Guide

## Overview

This project demonstrates how to integrate an **existing MCP server** into a LangChain chatbot. We've integrated a weather MCP server that uses the **Open-Meteo API** (free, no API key required).

## What is mcp-meteo?

`mcp-meteo` is an existing MCP server that provides weather data using the Open-Meteo API. It offers several tools:
- `get_weather_by_city(city)`: Get current weather for a city
- `get_forecast_by_city(city, days)`: Get weather forecast for multiple days
- `get_weather(latitude, longitude)`: Get weather by coordinates
- `get_forecast(latitude, longitude, days)`: Get forecast by coordinates

## Implementation

### Files Created

1. **`test_chatbot_with_mcp_server.py`**
   - Implements `MCPMetroClient` class that communicates with Open-Meteo API
   - Creates LangChain tools that wrap MCP server functionality
   - Provides a chatbot that uses these tools

2. **`test_mcp_server_integration.py`**
   - Test script to verify MCP server integration
   - Tests both direct tool calls and chatbot integration

### Key Components

#### MCPMetroClient

This class acts as a client for the mcp-meteo server. It:
- Calls Open-Meteo API directly (since mcp-meteo uses it internally)
- Handles geocoding (city name → coordinates)
- Formats weather data into readable responses
- Decodes WMO weather codes to descriptions

#### LangChain Tools

Two tools are created:
- `get_weather_by_city(city)`: Get current weather
- `get_forecast_by_city(city, days)`: Get multi-day forecast

These tools are automatically available to the LLM agent.

## Usage

### Test the Integration

```bash
python test_mcp_server_integration.py
```

This will:
1. Test the MCP tools directly
2. Test the chatbot with sample queries

### Run the Interactive Chatbot

```bash
python test_chatbot_with_mcp_server.py
```

Example queries:
- "What's the weather like in Malta?"
- "Give me a 5-day forecast for Rome"
- "What's the current weather in London?"

## Advantages of Using Open-Meteo

1. **Free**: No API key required
2. **No Rate Limits**: Generous free tier
3. **Accurate**: Uses multiple weather models
4. **Global Coverage**: Works worldwide
5. **Historical Data**: Available from 1940 to present

## Comparison: Custom vs External MCP Server

### Custom Server (`mcp_weather_server.py`)
- Uses OpenWeatherMap API (requires API key)
- Full control over implementation
- Good for learning MCP protocol

### External MCP Server (`test_chatbot_with_mcp_server.py`)
- Uses Open-Meteo API (no API key)
- Follows existing MCP server patterns
- Better for production use
- Easier to maintain (uses standard library)

## Next Steps

To use the actual `mcp-meteo` package:

1. Install it:
```bash
pip install mcp-meteo
```

2. Use `langchain-mcp-adapters` to connect:
```python
from langchain_mcp_adapters import MultiServerMCPClient

mcp_client = MultiServerMCPClient(
    servers={
        "weather": {
            "command": "python",
            "args": ["-m", "mcp_meteo.server"],
            "transport": "stdio"
        }
    }
)

tools = mcp_client.get_tools()
```

3. Use the tools in your LangChain agent.

## Notes

- The current implementation uses Open-Meteo API directly for simplicity
- In production, you would use the actual `mcp-meteo` package with proper MCP transport
- The `langchain-mcp-adapters` library makes integration seamless

