"""
Example of using MCP client with langchain-mcp-adapters

This demonstrates how to use the langchain-mcp-adapters library
to convert MCP tools to LangChain tools.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load environment variables
load_dotenv()

# Note: This example shows the concept. In practice, you would:
# 1. Set up an actual MCP server (using stdio, SSE, or HTTP transport)
# 2. Use langchain-mcp-adapters to connect to it
# 3. Convert MCP tools to LangChain tools

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    
    def create_mcp_chatbot():
        """Create a chatbot using MCP tools via langchain-mcp-adapters."""
        
        # Initialize the LLM
        llm = ChatOpenAI(
            model="gpt-5.1",
            temperature=0.7
        )
        
        # Create MCP client
        # In a real scenario, you would configure this to connect to your MCP server
        # For example:
        # mcp_client = MultiServerMCPClient(
        #     servers={
        #         "weather": {
        #             "command": "python",
        #             "args": ["mcp_weather_server.py"],
        #             "transport": "stdio"
        #         }
        #     }
        # )
        
        # Convert MCP tools to LangChain tools
        # tools = mcp_client.get_tools()
        
        # For this example, we'll use a direct tool instead
        # In production, use the MCP client above
        from mcp_weather_server import WeatherMCPServer
        from test_chatbot import SimpleAgent
        
        weather_server = WeatherMCPServer()
        
        @tool
        def get_weather_forecast(location: str, days: int = 1) -> str:
            """Get weather forecast for a location."""
            result = weather_server.get_weather_forecast(location, days)
            if "error" in result:
                return f"Error: {result['error']}"
            
            current = result["current"]
            response = f"Weather for {result['location']}:\n"
            response += f"Temperature: {current['temperature']}°C\n"
            response += f"Description: {current['description']}\n"
            response += f"Humidity: {current['humidity']}%\n"
            return response
        
        tools = [get_weather_forecast]
        
        # Create simple agent (using the same approach as test_chatbot)
        return SimpleAgent(llm, tools)

    def main():
        """Main function."""
        print("MCP Client Example")
        print("=" * 60)
        print("This demonstrates MCP tool integration with LangChain.")
        print("Note: For full MCP integration, configure MultiServerMCPClient")
        print("to connect to your MCP server.\n")
        
        if not os.getenv("OPENAI_API_KEY"):
            print("ERROR: OPENAI_API_KEY not found")
            return
        
        chatbot = create_mcp_chatbot()
        
        # Test query
        print("Testing with query: 'What's the weather in Malta?'\n")
        response = chatbot.invoke({
            "input": "What's the weather in Malta?",
            "chat_history": []
        })
        
        print(f"\nResponse: {response['output']}")
        
except ImportError:
    print("langchain-mcp-adapters not installed.")
    print("Install it with: pip install langchain-mcp-adapters")
    print("\nFor now, using direct tool implementation instead.")

