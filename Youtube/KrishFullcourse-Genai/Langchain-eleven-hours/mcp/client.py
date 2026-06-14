import asyncio

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()


async def main():
    client = MultiServerMCPClient({
        "math": {
            "command": "python",
            "args": ["mcp/mathsserver.py"],
            "transport": "stdio",
        },
        "weather": {
            "url": "http://localhost:8000/mcp",
            "transport": "streamable-http",
        },
    })
    tools = await client.get_tools()
    model = ChatGroq(model="qwen/qwen3-32b", temperature=0.0)
    agent = create_react_agent(model=model, tools=tools)
    math_response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "What is 5 + 7?"}]
    })
    print("Math response:", math_response["messages"][-1].content)


asyncio.run(main())
