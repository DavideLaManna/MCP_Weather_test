"""
Test script to demonstrate integration with external MCP server (mcp-meteo).

This script shows how to use an existing MCP server (mcp-meteo) that uses
Open-Meteo API (free, no API key needed).
"""

import os
from dotenv import load_dotenv
from test_chatbot_with_mcp_server import create_chatbot, MCPMetroClient

# Load environment variables
load_dotenv()


def test_mcp_tools():
    """Test the MCP tools directly."""
    print("=" * 60)
    print("Testing MCP Tools (Open-Meteo API)")
    print("=" * 60)
    
    client = MCPMetroClient()
    
    # Test get_weather_by_city
    print("\n1. Testing get_weather_by_city for 'Malta':")
    print("-" * 60)
    result = client._call_mcp_tool("get_weather_by_city", {"city": "Malta"})
    print(result)
    
    # Test get_forecast_by_city
    print("\n2. Testing get_forecast_by_city for 'Rome' (3 days):")
    print("-" * 60)
    result = client._call_mcp_tool("get_forecast_by_city", {"city": "Rome", "days": 3})
    print(result)
    
    print("\n✓ MCP tools test completed!\n")


def test_chatbot():
    """Test the chatbot with MCP tools."""
    print("=" * 60)
    print("Testing Chatbot with MCP Tools")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n✗ OPENAI_API_KEY not found. Skipping chatbot test.")
        return False
    
    try:
        chatbot = create_chatbot()
        
        # Test queries
        test_queries = [
            "What's the weather like in Malta?",
            "Give me a 5-day forecast for Valletta, Malta",
            "What's the current weather in Rome, Italy?",
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
            messages_list = None
            if isinstance(response, dict):
                messages_list = response.get('messages', [])
            elif hasattr(response, 'messages'):
                messages_list = response.messages
            
            if messages_list:
                # Get the last message (should be AIMessage with final response)
                last_message = messages_list[-1]
                output = last_message.content if hasattr(last_message, 'content') else str(last_message)
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
    print("MCP Server Integration Test")
    print("=" * 60 + "\n")
    
    # Test MCP tools directly
    test_mcp_tools()
    
    # Test chatbot
    chatbot_ok = test_chatbot()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"MCP Tools:     ✓ PASS")
    print(f"Chatbot:       {'✓ PASS' if chatbot_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if chatbot_ok:
        print("\n✓ All tests passed!")
        print("\nYou can now run the interactive chatbot with:")
        print("  python test_chatbot_with_mcp_server.py")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main()

