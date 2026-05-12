import  asyncio
from aiogram.exceptions import TelegramBadRequest
from database.engine import bot_session_maker
from database.orm_query import add_tender
from ai.agent import chat_chain
from foundation import parse_gz_deals, active_tasks
from tg_bot.url_up import get_page_url
from tg_bot.keyboards import start_kb, stop_kb


async def send_long_message(message, text: str):
    limit = 4096
    for i in range(0, len(text), limit):
        chunk = text[i:i + limit]
        try:
            await message.answer(chunk)
        except TelegramBadRequest:
            await message.answer(chunk, parse_mode=None)


async def run_analysis(message, user_id, base_url, prompt):
    try:
        page = 1
        while True:
            url = get_page_url(base_url, page)
            soup = await parse_gz_deals(url)
            if isinstance(soup, str):
                await message.answer(f'Возможно неправильная ссылка {base_url}, или портал ГЗ сейчас не работает. Проверьте и попробуйте позже',
                                     reply_markup=stop_kb)
                break

            table = soup.find("table", {"id": "search-result"})
            if table is None:
                page = 1
                continue

            deals = table.find_all('tr')

            for deal in deals:
                # Таблица пустая — все страницы пройдены
                if deal.find('td', {'class': "dataTables_empty"}):
                    page = 0
                    break

                number_td = deal.find('td')
                if not number_td:
                    continue
                strong = number_td.find('strong')
                if not strong:
                    continue
                number = strong.text.strip()

                link_tag = deal.find('a', href=True)
                if not link_tag:
                    continue

                deal_url = f'https://goszakup.gov.kz{link_tag.get("href")}'
                async with bot_session_maker() as session:
                    tender = await add_tender(session=session, user_id=user_id,
                                          number=number, url=deal_url)
                if tender:

                    user_message = (
                        f"{tender.url} это ссылка на госзакупку. "
                        f"Проанализируй ее, чтобы ответить на запрос: {prompt}"
                    )
                    answer = await chat_chain(user_message, tender.number)
                    if "False" in answer:
                        print(f"Пропущено {tender.url}")
                        continue
                    await send_long_message(message, f'{deal_url}\n{answer}')

                    await asyncio.sleep(10)

            page += 1

    except asyncio.CancelledError:
        pass  # задача отменена — выходим тихо
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=start_kb)
    finally:
        active_tasks.pop(user_id, None)