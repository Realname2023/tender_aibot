from aiogram import types, Router
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import add_user
from tg_bot.keyboards import start_kb

start_router=Router()

@start_router.message(CommandStart())
async def command_start_handler(message: types.Message, session: AsyncSession) -> None:

    user = message.from_user
    await add_user(
        session=session,
        user_id=user.id,
        full_name=user.full_name,
        user_name=user.username,
    )

    await message.answer('Нажми "/Начать_анализ_ГЗ"', reply_markup=start_kb)
