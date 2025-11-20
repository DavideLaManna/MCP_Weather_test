"""
Simple MCP Weather Server

This server provides weather forecast tools via the Model Context Protocol (MCP).
It uses OpenWeatherMap API to fetch weather data.
"""

import os
import json
from typing import Any
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


class WeatherMCPServer:
    """Simple MCP server for weather forecasts."""
    
    def __init__(self):
        self.api_key = OPENWEATHERMAP_API_KEY
        if not self.api_key:
            raise ValueError("OPENWEATHERMAP_API_KEY not found in environment variables")
    
    def get_weather_forecast(self, location: str, days: int = 1) -> dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location: City name or "city,country" format
            days: Number of days for forecast (1-5)
        
        Returns:
            Dictionary with weather forecast data
        """
        try:
            # Get current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            response.raise_for_status()
            current_data = response.json()
            
            # Get forecast if days > 1
            forecast_data = None
            if days > 1:
                forecast_url = f"http://api.openweathermap.org/data/2.5/forecast"
                forecast_response = requests.get(forecast_url, params=params, timeout=10)
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()
            
            # Format response
            result = {
                "location": location,
                "current": {
                    "temperature": current_data["main"]["temp"],
                    "feels_like": current_data["main"]["feels_like"],
                    "humidity": current_data["main"]["humidity"],
                    "pressure": current_data["main"]["pressure"],
                    "description": current_data["weather"][0]["description"],
                    "wind_speed": current_data.get("wind", {}).get("speed", 0),
                    "wind_direction": current_data.get("wind", {}).get("deg", 0),
                },
                "forecast_days": days
            }
            
            if forecast_data:
                # Extract forecast for the requested days
                forecast_list = []
                for item in forecast_data["list"][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                    forecast_list.append({
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"],
                    })
                result["forecast"] = forecast_list
            
            return result
            
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Failed to fetch weather data: {str(e)}",
                "location": location
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "location": location
            }
    
    def list_tools(self) -> list[dict[str, Any]]:
        """List available tools."""
        return [
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a specific location. Returns current weather and forecast for up to 5 days.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or 'city,country' format (e.g., 'Malta' or 'Valletta,MT')"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days for forecast (1-5)",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 5
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    
    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call a tool by name with arguments."""
        if name == "get_weather_forecast":
            location = arguments.get("location")
            days = arguments.get("days", 1)
            if not location:
                return {"error": "location parameter is required"}
            return self.get_weather_forecast(location, days)
        else:
            return {"error": f"Unknown tool: {name}"}


# Simple MCP protocol handler (simplified version)
async def handle_mcp_request(server: WeatherMCPServer, request: dict[str, Any]) -> dict[str, Any]:
    """Handle MCP protocol requests."""
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "tools/list":
        return {
            "tools": server.list_tools()
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        result = server.call_tool(tool_name, arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }
    else:
        return {"error": f"Unknown method: {method}"}


if __name__ == "__main__":
    print("Starting Weather MCP Server...")
    print("This is a simplified MCP server implementation.")
    print("For production use, consider using the official MCP SDK.\n")
    
    server = WeatherMCPServer()
    
    # Test the server
    print("Testing weather forecast for Malta...")
    result = server.get_weather_forecast("Malta", days=2)
    print(json.dumps(result, indent=2))
    
    print("\nAvailable tools:")
    tools = server.list_tools()
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")

