from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton


start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/Начать_анализ_ГЗ')],
], resize_keyboard=True)

stop_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/Остановить_анализ_ГЗ')],
], resize_keyboard=True)
# app_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Заказать товары',
#                           web_app=WebAppInfo(url='https://vtgas.pp.ua'))],
#                           [InlineKeyboardButton(text='Написать оператору', url='https://t.me/VTGonlinebot')]],
#                           resize_keyboard=True)
