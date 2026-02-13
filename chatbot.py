"""
MCP Weather Chatbot

Connects to the weather MCP server via stdio, loads tools with langchain-mcp-adapters,
and runs a ReAct-style agent. Uses Open-Meteo (free, no API key) for weather data.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()

# Resolve path to the weather MCP server
PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = str(PROJECT_ROOT / "server" / "weather.py")


def get_server_params() -> StdioServerParameters:
    """Configure the connection to the weather MCP server."""
    return StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None,
    )


def _extract_output(result: dict) -> str:
    """Extract final text from agent response."""
    messages = result.get("messages", [])
    if messages:
        last = messages[-1]
        if hasattr(last, "content"):
            return last.content or ""
        return str(last)
    return str(result)


async def run_query(agent, user_input: str) -> str:
    """Invoke the agent with a single query."""
    result = await agent.ainvoke({
        "messages": [HumanMessage(content=user_input)],
    })
    return _extract_output(result)


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    server_params = get_server_params()
    llm = ChatOpenAI(model="gpt-5.2", temperature=0)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=(
                    "You are a helpful assistant that provides weather forecasts using the available tools. "
                    "Use get_weather_by_city for current conditions and get_forecast_by_city for multi-day forecasts. "
                    "Be concise and format weather information clearly."
                ),
            )

            print("MCP Weather Chatbot (Open-Meteo, no API key)")
            print("Type 'quit' or 'exit' to end.\n")

            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if user_input.lower() in ("quit", "exit", "q"):
                    print("Goodbye.")
                    break
                if not user_input:
                    continue

                output = await run_query(agent, user_input)
                print(f"\nAssistant: {output}\n")


if __name__ == "__main__":
    asyncio.run(main())
