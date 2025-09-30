import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from deepagents import create_deep_agent, async_create_deep_agent

from langchain_ollama import ChatOllama

llm = ChatOllama(model="gpt-oss:latest",temperature=1)
async def main():
    client = MultiServerMCPClient(
        {
            "user_data": {
                "transport": "streamable_http",  # HTTP-based remote server
                # Ensure you start your weather server on port 8000
                "url": "http://localhost:7999/mcp",
            }
        }
    )
    tools= await client.get_tools()
    custom_subagent = {
        "name": "user_info_agent",
        "description": "Gets user info using available tools",
        "prompt": "You are a specialized agent to get info about users",
        "tools": tools
    }

    deep_agent = async_create_deep_agent(
        model=llm,
        instructions="You are an assistant who helps users redirecting to the correct agents",
        subagents=[custom_subagent],
        checkpointer=InMemorySaver(),
    )

    common_config = {"configurable": {"thread_id": "1"}}
    
    while True:
        user_question = input("Enter your question: ")
        result= await deep_agent.ainvoke({"messages": [HumanMessage(content=user_question)]},common_config, stream_mode="values")
        print(result)
    
if __name__ == "__main__":
    asyncio.run(main())    