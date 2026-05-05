import asyncio
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from foundation import llm
from ai.tools import agent_tools

checkpointer = InMemorySaver()

agent = create_agent(
    model = llm,
    tools = agent_tools,
    system_prompt="""Ты ассистент по анализу госзакупок Казахстана для поставщиков.
            Порядок работы:
            1. Получи общие сведения: get_deal_info
            2. Получи данные лотов: get_deal_lots  
            3. Получи документацию: get_deal_docs_info
            4. Если есть сканы/картинки: get_deal_docs_images
            5. Сделай итоговый анализ
            Итоговый ответ всегда должен содержать общие сведения и данные лотов.
            В общих сведениях обязательны организатор, название объявления, сумма и срок окончания приема заявок.
            Отвечай КРАТКО. Итоговый ответ не более 3000 символов.""",
    checkpointer=checkpointer
)

async def chat_chain(user_message: str, thread_id: str) -> str:
    max_retries = 5
    delay = 15

    for attempt in range(max_retries):
        try:
            response = await agent.ainvoke(
                {"messages": [{"role": "user", "content": user_message}]},
                {"configurable": {"thread_id": thread_id}}
            )
            return response["messages"][-1].content

        except Exception as e:
            error_str = str(e)
            # Ловим все серверные ошибки
            if any(code in error_str for code in ['503', '500', '429', 'overloaded', 'Internal Server']):
                if attempt < max_retries - 1:
                    print(f"Ошибка сервера: {e}. Повтор через {delay} сек... ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(delay)
                    delay *= 2  # 15 → 30 → 60 → 120 → 240
                else:
                    return f"Сервер недоступен после {max_retries} попыток. Попробуй позже."
            else:
                return f"Ошибка: {e}"
