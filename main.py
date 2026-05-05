import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
# from aiogram import types
# from typing import Union, Dict, Any
# from aiogram.filters import BaseFilter
# from aiogram.types import Message
from foundation import TG_BOT_TOKEN
from tg_bot.start import start_router
from tg_bot.client import client_router
from tg_bot.middlevares import DataBaseSession
from database.engine import bot_session_maker, create_db


bot = Bot(token=TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


# class WebAppDataFilter(BaseFilter):
#     async def __call__(self, message: Message, **kwargs) -> Union[bool, Dict[str, Any]]:
#         return dict(web_app_data=message.web_app_data) if message.web_app_data else False
#
#
# @dp.message(WebAppDataFilter())
# async def handle_web_app_data(message: types.Message,
#                               web_app_data: types.WebAppData):
#     print(web_app_data)
#     await message.answer("Received web app data")


dp.include_router(start_router)
dp.include_router(client_router)

# dp.include_router(group_router)


async def on_startup(bot):
    await create_db()
    print('бот запущен')


async def on_shutdown(bot):
    print('бот лег')


async def main() -> None:
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=bot_session_maker))
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
