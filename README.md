# MCP Weather Test Chatbot

This is an isolated test project to demonstrate MCP (Model Context Protocol) server integration with LangChain.

## Overview

This project includes:
1. A simple weather MCP server that provides weather forecasts
2. An MCP client to connect to the server
3. A test chatbot that uses the weather tool via LangChain

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenWeatherMap API key (free at https://openweathermap.org/api):
```bash
export OPENWEATHERMAP_API_KEY=your_api_key_here
```

Or create a `.env` file:
```
OPENWEATHERMAP_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
```

## Running the Components

### Option 1: Run MCP Server and Chatbot Separately

1. Start the MCP server:
```bash
python mcp_weather_server.py
```

2. In another terminal, run the chatbot:
```bash
python test_chatbot.py
```

### Option 2: Run Integrated Test (Recommended)

Run the integrated test that starts everything together:
```bash
python integrated_test.py
```

### Option 3: Test with External MCP Server (Open-Meteo)

Test the chatbot with external MCP server using Open-Meteo API (free, no API key needed):
```bash
python test_mcp_server_integration.py
```

Or run the interactive chatbot:
```bash
python test_chatbot_with_mcp_server.py
```

## Architecture

- **mcp_weather_server.py**: Simple MCP server that provides weather tools (using OpenWeatherMap)
- **test_chatbot.py**: Test chatbot using LangChain with custom MCP weather tool
- **test_chatbot_with_mcp_server.py**: Test chatbot using external MCP server (mcp-meteo compatible, using Open-Meteo API)
- **test_mcp_server_integration.py**: Test script for external MCP server integration
- **mcp_client_example.py**: Example showing MCP client integration patterns
- **integrated_test.py**: All-in-one test script

## Notes

This is a proof-of-concept implementation for learning MCP integration with LangChain. The weather server uses OpenWeatherMap's free API tier.

