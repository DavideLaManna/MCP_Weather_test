# Usage Guide

## Quick Start

1. **Install dependencies:**

```bash
cd mcp_weather_test
pip install -r requirements.txt
```

2. **Set up API keys:**
   Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_key
OPENWEATHERMAP_API_KEY=your_openweathermap_key
```

Get a free OpenWeatherMap API key at: https://openweathermap.org/api

3. **Run the integrated test:**

```bash
python integrated_test.py
```

4. **Run the interactive chatbot:**

```bash
python test_chatbot.py
```

## Architecture Overview

### Components

1. **Weather MCP Server** (`mcp_weather_server.py`)

   - Provides weather forecast functionality
   - Implements MCP protocol structure
   - Uses OpenWeatherMap API
2. **Test Chatbot** (`test_chatbot.py`)

   - LangChain agent with weather tool
   - Interactive chat interface
   - Uses OpenAI GPT-5.1 model
3. **MCP Client Example** (`mcp_client_example.py`)

   - Shows how to use langchain-mcp-adapters (when available)
   - Demonstrates MCP tool integration pattern
4. **Integrated Test** (`integrated_test.py`)

   - Tests all components together
   - Validates the complete integration

## How It Works

1. **Weather Server**: The `WeatherMCPServer` class provides weather data by calling OpenWeatherMap API. It exposes tools via MCP-compatible interface.
2. **LangChain Tool**: The weather server is wrapped as a LangChain tool using the `@tool` decorator, making it available to the LLM agent.
3. **Agent**: The chatbot uses a LangChain agent that can automatically decide when to use the weather tool based on user queries.

## Example Queries

- "What's the weather in Malta?"
- "Tell me about the weather forecast for Valletta for the next 3 days"
- "How's the weather in Rome, Italy?"

## MCP Integration Notes

This implementation demonstrates:

- Creating an MCP-compatible server structure
- Converting MCP tools to LangChain tools
- Using tools in a LangChain agent

For production use with full MCP protocol support, consider:

- Using the official MCP Python SDK
- Setting up proper MCP transport (stdio, SSE, or HTTP)
- Using `langchain-mcp-adapters` for seamless integration

## Troubleshooting

**Error: OPENWEATHERMAP_API_KEY not found**

- Make sure you've created a `.env` file with your API key
- Get a free API key from https://openweathermap.org/api

**Error: OPENAI_API_KEY not found**

- Add your OpenAI API key to the `.env` file

**Weather API errors**

- Check your OpenWeatherMap API key is valid
- Verify you haven't exceeded the free tier rate limits
- Check the location name format (try "city,country" format)
