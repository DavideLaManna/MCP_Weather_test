"""
Integrated Test Script

This script demonstrates the complete MCP weather integration:
1. Weather MCP Server functionality
2. LangChain tool integration
3. Chatbot interaction
"""

import os
from dotenv import load_dotenv
from mcp_weather_server import WeatherMCPServer
from test_chatbot import create_chatbot

# Load environment variables
load_dotenv()


def test_weather_server():
    """Test the weather server directly."""
    print("=" * 60)
    print("Testing Weather MCP Server")
    print("=" * 60)
    
    try:
        server = WeatherMCPServer()
        
        # Test weather forecast
        print("\n1. Testing weather forecast for Malta...")
        result = server.get_weather_forecast("Malta", days=2)
        
        if "error" in result:
            print(f"   Error: {result['error']}")
        else:
            current = result["current"]
            print(f"   Location: {result['location']}")
            print(f"   Current Temperature: {current['temperature']}°C")
            print(f"   Description: {current['description']}")
            print(f"   Humidity: {current['humidity']}%")
            print(f"   Wind Speed: {current['wind_speed']} m/s")
        
        # List available tools
        print("\n2. Available MCP tools:")
        tools = server.list_tools()
        for tool in tools:
            print(f"   - {tool['name']}")
            print(f"     Description: {tool['description']}")
        
        print("\n✓ Weather server test completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Weather server test failed: {e}\n")
        return False


def test_chatbot():
    """Test the chatbot with weather tool."""
    print("=" * 60)
    print("Testing Chatbot with Weather Tool")
    print("=" * 60)
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("\n✗ OPENAI_API_KEY not found. Skipping chatbot test.")
        return False
    
    if not os.getenv("OPENWEATHERMAP_API_KEY"):
        print("\n✗ OPENWEATHERMAP_API_KEY not found. Skipping chatbot test.")
        return False
    
    try:
        chatbot = create_chatbot()
        
        # Test queries
        test_queries = [
            "What's the weather like in Malta?",
            "Tell me about the weather forecast for Valletta, Malta for the next 3 days",
        ]
        
        from langchain_core.messages import HumanMessage
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            print("-" * 60)
            
            response = chatbot.invoke({
                "messages": [HumanMessage(content=query)]
            })
            
            # Extract the response content from the last AIMessage
            # response can be a dict or an object with messages attribute
            messages = None
            if isinstance(response, dict):
                messages = response.get('messages', [])
            elif hasattr(response, 'messages'):
                messages = response.messages
            
            if messages:
                # Get the last message (should be AIMessage with final response)
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    output = last_message.content
                else:
                    output = str(last_message)
            elif hasattr(response, 'content'):
                output = response.content
            else:
                output = str(response)
            
            print(f"Response: {output}\n")
        
        print("✓ Chatbot test completed successfully!\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Chatbot test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MCP Weather Integration - Integrated Test")
    print("=" * 60 + "\n")
    
    # Test weather server
    server_ok = test_weather_server()
    
    # Test chatbot
    chatbot_ok = test_chatbot()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Weather Server: {'✓ PASS' if server_ok else '✗ FAIL'}")
    print(f"Chatbot:        {'✓ PASS' if chatbot_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if server_ok and chatbot_ok:
        print("\n✓ All tests passed!")
        print("\nYou can now run the interactive chatbot with:")
        print("  python test_chatbot.py")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()

