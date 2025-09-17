import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage

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
    agent=create_agent(model=llm,
                       prompt="You are an assistant who helps users using your tools",
                       tools=tools,
                       checkpointer=InMemorySaver(),
                       )
    common_config = {"configurable": {"thread_id": "1"}}

    response= await agent.ainvoke({"messsage":[{"role":"user","content":"showme the name of the user with  id = 1 ? "}]},common_config)
    print(f"------1--------------{response["messages"][-1].content}")
    response= await agent.ainvoke({"messsage":[{"role":"user","content":" the id of user is 1"}]},common_config)
    print(f"-------2--------------{response["messages"][-1].content}")
    response= await agent.ainvoke({"messsage":[{"role":"user","content":" yes"}]},common_config)
    print(f"-------3--------------{response["messages"][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())    