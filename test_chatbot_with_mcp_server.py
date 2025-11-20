"""
Test Chatbot with External MCP Server (mcp-meteo)

This chatbot demonstrates how to integrate an existing MCP server (mcp-meteo)
with LangChain. The mcp-meteo server uses Open-Meteo API (free, no API key needed).
"""

import os
import subprocess
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict, Any

# Load environment variables
load_dotenv()


class MCPMetroClient:
    """Client for mcp-meteo MCP server using subprocess communication."""
    
    def __init__(self):
        """Initialize the MCP client."""
        self.server_process = None
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call an MCP tool by executing the mcp-meteo server.
        
        Note: This is a simplified implementation. In production, you would
        use proper MCP client libraries or langchain-mcp-adapters.
        """
        try:
            # For this example, we'll use a direct API call to Open-Meteo
            # since mcp-meteo uses Open-Meteo API internally
            import requests
            
            if tool_name == "get_weather_by_city":
                city = arguments.get("city", "")
                # Use Open-Meteo geocoding to get coordinates
                geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
                geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
                geo_response = requests.get(geocode_url, params=geo_params, timeout=10)
                
                if geo_response.status_code != 200:
                    return f"Error: Could not find location {city}"
                
                geo_data = geo_response.json()
                if not geo_data.get("results"):
                    return f"Error: Could not find location {city}"
                
                result = geo_data["results"][0]
                latitude = result["latitude"]
                longitude = result["longitude"]
                
                # Get weather data
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                    "timezone": "auto"
                }
                weather_response = requests.get(weather_url, params=weather_params, timeout=10)
                
                if weather_response.status_code != 200:
                    return f"Error: Could not fetch weather data"
                
                weather_data = weather_response.json()
                current = weather_data.get("current", {})
                
                # Format response
                response = f"Weather for {city} ({result.get('name', '')}):\n"
                response += f"Temperature: {current.get('temperature_2m', 'N/A')}°C\n"
                response += f"Humidity: {current.get('relative_humidity_2m', 'N/A')}%\n"
                response += f"Wind Speed: {current.get('wind_speed_10m', 'N/A')} km/h\n"
                
                # Decode weather code
                weather_code = current.get('weather_code', 0)
                weather_desc = self._decode_weather_code(weather_code)
                response += f"Conditions: {weather_desc}\n"
                
                return response
                
            elif tool_name == "get_forecast_by_city":
                city = arguments.get("city", "")
                days = arguments.get("days", 7)
                
                # Get coordinates
                geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
                geo_params = {"name": city, "count": 1, "language": "en", "format": "json"}
                geo_response = requests.get(geocode_url, params=geo_params, timeout=10)
                
                if geo_response.status_code != 200:
                    return f"Error: Could not find location {city}"
                
                geo_data = geo_response.json()
                if not geo_data.get("results"):
                    return f"Error: Could not find location {city}"
                
                result = geo_data["results"][0]
                latitude = result["latitude"]
                longitude = result["longitude"]
                
                # Get forecast
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                    "forecast_days": min(days, 7),
                    "timezone": "auto"
                }
                weather_response = requests.get(weather_url, params=weather_params, timeout=10)
                
                if weather_response.status_code != 200:
                    return f"Error: Could not fetch forecast data"
                
                weather_data = weather_response.json()
                daily = weather_data.get("daily", {})
                
                # Format response
                response = f"Weather forecast for {city} ({result.get('name', '')}) - {days} days:\n\n"
                
                dates = daily.get("time", [])
                temps_max = daily.get("temperature_2m_max", [])
                temps_min = daily.get("temperature_2m_min", [])
                codes = daily.get("weather_code", [])
                
                for i in range(min(len(dates), days)):
                    date = dates[i]
                    temp_max = temps_max[i] if i < len(temps_max) else "N/A"
                    temp_min = temps_min[i] if i < len(temps_min) else "N/A"
                    code = codes[i] if i < len(codes) else 0
                    desc = self._decode_weather_code(code)
                    
                    response += f"{date}: {desc}, High: {temp_max}°C, Low: {temp_min}°C\n"
                
                return response
            else:
                return f"Error: Unknown tool {tool_name}"
                
        except Exception as e:
            return f"Error calling MCP tool: {str(e)}"
    
    def _decode_weather_code(self, code: int) -> str:
        """Decode WMO weather code to description."""
        codes = {
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
            99: "Thunderstorm with heavy hail"
        }
        return codes.get(code, f"Unknown weather code {code}")


# Initialize MCP client
mcp_client = MCPMetroClient()


@tool
def get_weather_by_city(city: str) -> str:
    """
    Get current weather for a city using Open-Meteo API (via mcp-meteo compatible interface).
    
    Args:
        city: City name (e.g., "Rome", "Malta", "London")
    
    Returns:
        String with current weather information
    """
    return mcp_client._call_mcp_tool("get_weather_by_city", {"city": city})


@tool
def get_forecast_by_city(city: str, days: int = 7) -> str:
    """
    Get weather forecast for a city for the next N days using Open-Meteo API.
    
    Args:
        city: City name (e.g., "Rome", "Malta", "London")
        days: Number of days for forecast (1-7), default is 7
    
    Returns:
        String with weather forecast information
    """
    return mcp_client._call_mcp_tool("get_forecast_by_city", {"city": city, "days": days})


def create_chatbot():
    """Create a chatbot with MCP weather tools using LangChain's create_agent."""
    
    # Initialize the LLM
    model = ChatOpenAI(
        model="gpt-5.1",
        temperature=0.7
    )
    
    # Create tools list (using Open-Meteo via mcp-meteo compatible interface)
    tools = [get_weather_by_city, get_forecast_by_city]
    
    # System prompt
    system_prompt = """You are a helpful assistant that can provide weather forecasts using Open-Meteo API.
When users ask about weather, use the available weather tools to get current and forecasted weather information.
Be friendly and provide clear, formatted weather information."""
    
    # Use LangChain's create_agent (standard way in LangChain 1.0)
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent


def main():
    """Main chat loop."""
    print("=" * 60)
    print("MCP Weather Test Chatbot (using Open-Meteo API)")
    print("=" * 60)
    print("This chatbot uses Open-Meteo API (free, no API key needed)")
    print("via mcp-meteo compatible interface.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        return
    
    # Create chatbot
    chatbot = create_chatbot()
    
    chat_history = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        try:
            # Convert chat history to LangChain message format
            messages = []
            for role, content in chat_history:
                if role == "human":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
            messages.append(HumanMessage(content=user_input))
            
            # Run the agent
            response = chatbot.invoke({
                "messages": messages
            })
            
            # Extract the response content from the last AIMessage
            # response can be a dict or an object with messages attribute
            messages_list = None
            if isinstance(response, dict):
                messages_list = response.get('messages', [])
            elif hasattr(response, 'messages'):
                messages_list = response.messages
            
            if messages_list:
                # Get the last message (should be AIMessage with final response)
                last_message = messages_list[-1]
                if hasattr(last_message, 'content'):
                    output = last_message.content
                else:
                    output = str(last_message)
            elif hasattr(response, 'content'):
                output = response.content
            else:
                output = str(response)
            
            print(f"\nAssistant: {output}")
            
            # Update chat history
            chat_history.append(("human", user_input))
            chat_history.append(("assistant", output))
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

