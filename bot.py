from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import Message, ParseMode
from aiogram.filters import Command
import asyncio

# Вставь токен, который выдал BotFather
API_TOKEN = '7550524826:AAHUiJoSnaJIgK74Ca2wDmXwDIaS_86PWWs'

# Идентификатор твоего чата в Telegram (можно узнать через @userinfobot или вручную)
ADMIN_CHAT_ID = 623455049

# Создание объекта бота
bot = Bot(token=API_TOKEN)

# Создание диспетчера
dp = Dispatcher(bot)


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я бот-помощник для Авито. Задай свой вопрос!")


# Ответ на любое сообщение
@dp.message()
async def handle_message(message: Message):
    user_message = message.text.lower()

    if "цена" in user_message:
        await message.answer("Цена набора: от 1000 до 2000 рублей. Уточните, какой вас интересует?")
    elif "доставка" in user_message:
        await message.answer("Доставка по Казани возможна. Напишите адрес для уточнения стоимости!")
    elif "самовывоз" in user_message:
        await message.answer("Самовывоз доступен в центре Казани. Уточните удобное время.")
    else:
        await message.answer("Я пока не знаю, как ответить на этот вопрос. Напишите подробнее!")

@dp.message_handler(lambda message: message.text.strip() == "1")
async def contact_admin(message: types.Message):
    user = message.from_user.username if message.from_user.username else "Без @username"
    admin_message = f"С вами хочет связаться @{user}."
    await bot.send_message(ADMIN_CHAT_ID, admin_message)
    await message.reply("Ваш запрос отправлен администратору. Ожидайте ответа!")

# Функция запуска бота
async def main():
    try:
        # Удаляем старые вебхуки
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем бота
        await dp.start_polling(bot)
    finally:
        # Закрываем сессию
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
