import aiohttp
import  asyncio
from os import getenv
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
from langchain_ollama import ChatOllama
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# DATABASE_URL = str(getenv('DB_URL'))
DATABASE_URL = f"postgresql+asyncpg://{getenv('POSTGRES_USER')}:{getenv('POSTGRES_PASSWORD')}@db:5432/{getenv('POSTGRES_DB')}"
TG_BOT_TOKEN = str(getenv('TG_BOT_TOKEN'))

llm = ChatOllama(model="gemma4:31b-cloud", host='http://ollama:11434')

#model = mistral-large-3:675b-cloud ministral-3:14b-cloud deepseek-v3.1:671b-cloud gpt-oss:120b-cloud, gpt-oss:20b-cloud, qwen3-next:80b-cloud ministral-3:8b-cloud ministral-3:3b-cloud "qwen2.5-coder:0.5b"

active_tasks: dict[int, asyncio.Task] = {}

async def parse_gz_deals(linc: str):
    async with aiohttp.ClientSession() as session:
        HEADERS = {"User-Agent": UserAgent().random}
        try:
            async with session.get(linc, headers=HEADERS) as response:
                if response.status == 200:
                    result = await response.text()
                    soup = BS(result, "html.parser")
                    return soup
                else:
                    return f"Ошибка {response.status} при загрузке {linc}"
        except Exception as e:
            return f"Ошибка запроса {linc}: {e}"


async def parse_bytes(linc: str):
    async with aiohttp.ClientSession() as session:
        HEADERS = {"User-Agent": UserAgent().random}
        try:
            async with session.get(linc, headers=HEADERS) as response:
                if response.status == 200:
                    result = await response.read()
                    return result
                else:
                    return f"Ошибка {response.status} при загрузке {linc}"
        except Exception as e:
            return f"Ошибка запроса {linc}: {e}"

# url_webhook = str(getenv("URL_WEBHOOK"))
#
# method_company_list = 'crm.company.list'
# method_company_add = 'crm.company.add'
# method_deal_add = 'crm.deal.add'
# method_todo_add = 'crm.activity.add'
# method_lead_add = 'crm.lead.add'
# # method_contact_update = 'crm.contact.update'
# method_products_set = 'crm.deal.productrows.set'
# method_products_set_to_lead = 'crm.lead.productrows.set'
# # method_contact_list = 'crm.contact.list'
# # method_contact_add = 'crm.contact.add'
# method_list_deals = 'crm.deal.list'
# method_list_leads = 'crm.lead.list'
# method_user_search = 'user.search'


# async def parse_sk_deals(linc: str):
#     HEADERS = {"User-Agent": UserAgent().random}
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(linc, headers=HEADERS) as response:
#                 if response.status == 200:
#                     result = await response.json()
#                     return result
#                 else:
#                     return f"Ошибка {response.status} при загрузке {linc}"
#         except Exception as e:
#             return f"Ошибка запроса {linc}: {e}"


# async def b24rest_request(url_webhook: str, method: str, parametr: dict) -> dict:
#     url = url_webhook + method + '.json?'
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, json=parametr) as response:
#             response_data = await response.json()
#             if response.status == 200:
#                 # Запрос выполнен успешно
#                 print(f"Ответ сервера: {response_data}")
#             else:
#                 print(f"Ошибка при выполнении запроса. Статус код: {response_data}")
#     return response_data
