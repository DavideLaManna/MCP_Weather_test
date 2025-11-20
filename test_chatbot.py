"""
Test Chatbot with MCP Weather Tool

This chatbot demonstrates how to use MCP weather tools with LangChain.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from mcp_weather_server import WeatherMCPServer

# Load environment variables
load_dotenv()

# Initialize weather server
weather_server = WeatherMCPServer()


@tool
def get_weather_forecast(location: str, days: int = 1) -> str:
    """
    Get weather forecast for a specific location.
    
    Args:
        location: City name or "city,country" format (e.g., "Malta" or "Valletta,MT")
        days: Number of days for forecast (1-5), default is 1
    
    Returns:
        String with formatted weather forecast information
    """
    result = weather_server.get_weather_forecast(location, days)
    
    if "error" in result:
        return f"Error: {result['error']}"
    
    # Format the response
    current = result["current"]
    response = f"Weather forecast for {result['location']}:\n\n"
    response += f"Current conditions:\n"
    response += f"  Temperature: {current['temperature']}°C (feels like {current['feels_like']}°C)\n"
    response += f"  Description: {current['description']}\n"
    response += f"  Humidity: {current['humidity']}%\n"
    response += f"  Pressure: {current['pressure']} hPa\n"
    response += f"  Wind: {current['wind_speed']} m/s"
    
    if result.get("forecast"):
        response += f"\n\nForecast for the next {result['forecast_days']} day(s):\n"
        for i, forecast_item in enumerate(result["forecast"][:result['forecast_days'] * 3], 1):
            response += f"  {forecast_item['datetime']}: {forecast_item['temperature']}°C, {forecast_item['description']}\n"
    
    return response


def create_chatbot():
    """Create a chatbot with weather tool using LangChain's create_agent."""
    
    # Initialize the LLM
    model = ChatOpenAI(
        model="gpt-5.1",
        temperature=0.7
    )
    
    # Create tools list
    tools = [get_weather_forecast]
    
    # System prompt
    system_prompt = """You are a helpful assistant that can provide weather forecasts.
When users ask about weather, use the get_weather_forecast tool to get current and forecasted weather information.
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
    print("MCP Weather Test Chatbot")
    print("=" * 60)
    print("This chatbot can answer questions about weather forecasts.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        return
    
    if not os.getenv("OPENWEATHERMAP_API_KEY"):
        print("ERROR: OPENWEATHERMAP_API_KEY not found in environment variables")
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
            from langchain_core.messages import HumanMessage, AIMessage
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


if __name__ == "__main__":
    main()

