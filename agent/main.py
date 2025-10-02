import asyncio
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage
from deepagents import create_deep_agent, async_create_deep_agent
from langchain.chat_models import init_chat_model

from langchain_ollama import ChatOllama

llm = init_chat_model(model="ollama:gpt-oss:latest",temperature=1)
async def main():
   # 1. Conectar al servidor MCP y obtener herramientas
    client = MultiServerMCPClient(
        {
            "user_data": {
                "transport": "streamable_http",
                "url": "http://localhost:7999/mcp",
            }
        }
    )
    
    tools = await client.get_tools()
    print(f"✓ Herramientas disponibles: {[t.name for t in tools]}\n")
    
    # 2. Crear un grafo personalizado para el subagente usando create_agent
    # Este subagente TENDRÁ las herramientas y las ejecutará
    user_info_agent_graph = create_agent(
        model=llm,
        tools=tools,  # ← El subagente tiene las herramientas
        prompt="You are a specialized agent for getting user information. Use your tools to retrieve and provide accurate user data.",
    )
    
    # 3. Definir el CustomSubAgent (con grafo personalizado)
    custom_subagent = {
        "name": "user_info_agent",
        "description": "Specialized agent that has tools to get user information, profiles, and data. Use this agent when you need to retrieve or query user-related information.",
        "graph": user_info_agent_graph  # ← Usar 'graph' en lugar de 'prompt' y 'tools'
    }

    # 4. Crear el deep_agent sin herramientas (solo como orquestador)
    deep_agent = async_create_deep_agent(
        model=llm,
        tools=[],  # ← Sin herramientas propias, solo delega
        instructions="""You are a routing assistant that delegates tasks to specialized agents.

You DO NOT have direct access to tools. Instead, you have access to specialized subagents:

- **user_info_agent**: Use this agent for ANY question about users, user data, profiles, or user information.

Your job is to:
1. Understand what the user is asking for
2. Identify which specialized agent should handle the request
3. Delegate to that agent by calling it
4. Return the results to the user

IMPORTANT: You must delegate to the appropriate subagent. Do not try to answer questions directly if a subagent should handle them.""",
        subagents=[custom_subagent],
        checkpointer=InMemorySaver(),
    )

    common_config = {"configurable": {"thread_id": "1"}}
    
    print("🤖 Deep Agent Router listo. El agente delegará a subagentes especializados.\n")
    
    try:
        while True:
            user_question = input("Tú: ")
            
            if user_question.lower() in ['salir', 'exit', 'quit']:
                break
            
            if not user_question.strip():
                continue
            
            print("\n" + "="*60)
            print("Procesando...\n")
            
            async for chunk in deep_agent.astream(
                {"messages": [HumanMessage(content=user_question)]},
                common_config,
                stream_mode="values"
            ):
                if "messages" in chunk:
                    last_msg = chunk["messages"][-1]
                    
                    # Mostrar cuando se llama a un subagente
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        for tc in last_msg.tool_calls:
                            if 'agent' in tc['name'].lower():
                                print(f"🔀 Delegando a: {tc['name']}")
                    
                    # Mostrar respuestas
                    if hasattr(last_msg, 'content') and last_msg.content:
                        if last_msg.type == "ai":
                            print(f"\n🤖 Agente: {last_msg.content}")
            
            print("="*60 + "\n")
    
    finally:

        del deep_agent
        del custom_subagent
        del user_info_agent_graph
        del client

        print("\n✓ Sesión terminada")

if __name__ == "__main__":
    asyncio.run(main())    