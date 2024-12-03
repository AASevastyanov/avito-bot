import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Ваш токен от BotFather
API_TOKEN = '7550524826:AAHUiJoSnaJIgK74Ca2wDmXwDIaS_86PWWs'

# ID администратора, куда будут отправляться запросы
ADMIN_CHAT_ID = 623455049

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- Reply-клавиатура ---
reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)
reply_kb.add(
    KeyboardButton(text="1"),
    KeyboardButton(text="2"),
    KeyboardButton(text="3")
)

# --- Inline-клавиатура ---
inline_kb = InlineKeyboardMarkup(row_width=3)
inline_kb.add(
    InlineKeyboardButton(text="1", callback_data="button_1"),
    InlineKeyboardButton(text="2", callback_data="button_2"),
    InlineKeyboardButton(text="3", callback_data="button_3")
)

# --- Обработчики команд ---
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Вот что я могу:\n"
        "- Выберите вариант из меню ниже.\n"
        "- Либо используйте кнопки внутри сообщения:",
        reply_markup=reply_kb  # Reply-клавиатура
    )
    await message.answer(
        "Выберите из этого меню:",
        reply_markup=inline_kb  # Inline-клавиатура
    )

# --- Обработка Reply-кнопок ---
@dp.message(lambda message: message.text in ["1", "2", "3"])
async def process_reply_menu(message: Message):
    if message.text == "1":
        await message.answer("Вы выбрали 1")
    elif message.text == "2":
        await message.answer("Вы выбрали 2")
    elif message.text == "3":
        await message.answer("Вы выбрали 3")

# --- Обработка Inline-кнопок ---
@dp.callback_query()
async def process_inline_menu(callback_query):
    if callback_query.data == "button_1":
        await callback_query.message.answer("Вы нажали кнопку 1")
    elif callback_query.data == "button_2":
        await callback_query.message.answer("Вы нажали кнопку 2")
    elif callback_query.data == "button_3":
        await callback_query.message.answer("Вы нажали кнопку 3")
    await callback_query.answer()  # Закрыть уведомление

# --- Заглушка для Render ---
async def handle(request):
    return web.Response(text="Бот работает!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

# --- Основная функция запуска ---
async def main():
    print("Бот запущен...")
    loop = asyncio.get_event_loop()
    loop.create_task(start_server())  # Запуск заглушки для Render
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
