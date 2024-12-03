import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

# Ваш токен от BotFather
API_TOKEN = '7550524826:AAHUiJoSnaJIgK74Ca2wDmXwDIaS_86PWWs'

# ID администратора, куда будут отправляться запросы
ADMIN_CHAT_ID = 623455049

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот для Авито. Вот что я могу:\n"
        "- Напишите '1', чтобы запросить связь с администратором.\n"
        "- Задавайте любые вопросы, например: 'Цена', 'Доставка', 'Самовывоз'."
    )

# Обработка сообщений с цифрой "1"
@dp.message(lambda message: message.text.strip() == "1")
async def contact_admin(message: Message):
    user = message.from_user.username if message.from_user.username else "Без @username"
    admin_message = f"С вами хочет связаться @{user}."
    await bot.send_message(ADMIN_CHAT_ID, admin_message)
    await message.answer("Ваш запрос отправлен администратору. Ожидайте ответа!")

# Ответы на ключевые слова
@dp.message(lambda message: "цена" in message.text.lower())
async def handle_price(message: Message):
    await message.answer("Цена набора: от 1000 до 2000 рублей. Уточните, какой именно вас интересует?")

@dp.message(lambda message: "доставка" in message.text.lower())
async def handle_delivery(message: Message):
    await message.answer("Доставка по Казани возможна. Напишите адрес для уточнения стоимости!")

@dp.message(lambda message: "самовывоз" in message.text.lower())
async def handle_pickup(message: Message):
    await message.answer("Самовывоз доступен в центре Казани. Уточните удобное время.")

# Обработка неизвестных сообщений
@dp.message()
async def handle_unknown(message: Message):
    await message.answer("Я пока не знаю, как ответить на это. Напишите подробнее!")

# Заглушка для порта, чтобы Render не выдавал ошибку
async def handle(request):
    return web.Response(text="Бот работает!")

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

# Основная функция запуска бота
async def main():
    print("Бот запущен...")
    loop = asyncio.get_event_loop()
    loop.create_task(start_server())  # Запуск заглушки для Render
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())