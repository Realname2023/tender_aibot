import asyncio
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from foundation import active_tasks
from database.orm_query import delete_users_tenders
from tg_bot.states import GZState
from tg_bot.keyboards import start_kb, stop_kb
from tg_bot.url_up import extract_gz_url, convert_search_url
from tg_bot.analysis import run_analysis

client_router = Router()

@client_router.message(F.text == '/Остановить_анализ_ГЗ')
async def stop_analysis(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    user_id = message.from_user.id
    await delete_users_tenders(session, user_id)
    if user_id in active_tasks and not active_tasks[user_id].done():
        active_tasks[user_id].cancel()
        await message.answer('Анализ ГЗ остановлен', reply_markup=start_kb)
    else:
        await message.answer('Нет активного анализа', reply_markup=start_kb)

@client_router.message(F.text == '/Начать_анализ_ГЗ')
async def analysis_start_handler(message: types.Message, state: FSMContext) -> None:
    await message.answer('Отправь ссылку поиска ГЗ', reply_markup=stop_kb)
    await state.set_state(GZState.base_url)


@client_router.message(GZState.base_url)
async def get_base_url(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    url = extract_gz_url(text)
    if not url:
        await message.answer(
            "Ссылка не найдена. Отправь ссылку поиска госзакупок, например:\n"
            "https://goszakup.gov.kz/ru/search/announce?..."
        )
        return

    converted = convert_search_url(url)
    if not converted:
        await message.answer(
            "Ссылка найдена, но не удалось её обработать. Попробуй снова."
        )
        return

    await state.update_data(base_url=converted)  # сохраняем уже сконвертированную
    await message.answer('Теперь отправь промпт')
    await state.set_state(GZState.prompt)


@client_router.message(GZState.prompt)
async def get_prompt(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    prompt = message.text.strip()
    data = await state.get_data()
    base_url = data.get('base_url')
    await state.clear()

    # Отменяем предыдущую задачу если есть
    if user_id in active_tasks and not active_tasks[user_id].done():
        active_tasks[user_id].cancel()
        await message.answer("Предыдущий анализ остановлен. Начинаю новый...")

    await message.answer('Начинаю анализ ГЗ', reply_markup=stop_kb)

    task = asyncio.create_task(
        run_analysis(message, user_id, base_url, prompt)
    )
    active_tasks[user_id] = task


@client_router.message()
async def get_other_messages(message: types.Message):
    await message.answer('Бот занимается только анализом ГЗ. на другие сообщения не отвечает')
