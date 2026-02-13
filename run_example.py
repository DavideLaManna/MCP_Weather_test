"""
Single-query example: MCP server + LangChain agent.

Demonstrates the full flow: StdioServerParameters, stdio_client, ClientSession,
load_mcp_tools, and create_agent. Run once and exit.
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

PROJECT_ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = str(PROJECT_ROOT / "server" / "weather.py")


async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_SCRIPT],
        env=None,
    )
    llm = ChatOpenAI(model="gpt-5.2", temperature=0)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)

            agent = create_agent(
                model=llm,
                tools=tools,
                system_prompt=(
                    "You are a helpful weather assistant. Use the available tools to answer."
                ),
            )

            query = "What's the weather like in Malta?"
            print(f"Query: {query}\n")
            result = await agent.ainvoke({
                "messages": [HumanMessage(content=query)],
            })
            messages = result.get("messages", [])
            if messages:
                last = messages[-1]
                output = last.content if hasattr(last, "content") else str(last)
            else:
                output = str(result)
            print(f"Response: {output}")


if __name__ == "__main__":
    asyncio.run(main())
