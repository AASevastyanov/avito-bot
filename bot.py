import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, FSInputFile)
from aiogram.filters import Command, CommandObject
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
# Ваш токен от BotFather
API_TOKEN = os.getenv('API_TOKEN')
print(API_TOKEN)

# ID администратора, куда будут отправляться запросы
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

DEBUG = os.getenv('DEBUG', 'False')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ---------- Состояния ----------
class OrderStates(StatesGroup):
    waiting_for_order_info = State()

class QuestionStates(StatesGroup):
    waiting_for_question = State()

# ---------- Клавиатуры ----------
town_answers = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text = 'Да!', callback_data='main_menu')
        ],
        [
            InlineKeyboardButton(text='Другой город', callback_data='no_variant')
        ]
    ]
)

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1. Подробнее о наборах 🏠", callback_data="details"),
        ],
        [
            InlineKeyboardButton(text="2. Другой вопрос ❓", callback_data="other_question"),
        ],
        [
            InlineKeyboardButton(text="3. Оформить предзаказ 🎁", callback_data="preorder")
        ]
    ]
)

sets_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1. «Маленькое чудо ✨» (1000 руб)", callback_data="set_1"),
        ],
        [
            InlineKeyboardButton(text="2. «Тёплый снег ❄️» (1500 руб)", callback_data="set_2"),
        ],
        [
            InlineKeyboardButton(text="3. «Семейное волшебство 🪄» (2000 руб)", callback_data="set_3"),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="back_to_main")
        ]
    ]
)

def set_detail_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оформить заказ ✅", callback_data="order"),
                InlineKeyboardButton(text="Назад", callback_data="back_to_sets")
            ]
        ]
    )

order_confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да!", callback_data="order_yes"),
            InlineKeyboardButton(text="Я подумаю", callback_data="order_think_again")
        ]
    ]
)

other_question_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ]
)

after_order_main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Главное меню", callback_data="back_to_main")]
    ]
)


# ---------- Данные о наборах ----------
sets_data = {
    "set_1": {
        "name": "Маленькое чудо",
        "price": 1000,
        "description": (
            "Набор «Маленькое чудо ✨» (1000 руб):\n"
            "• 🥮Имбирный человечек\n"
            "• 🥮Имбирное печенье (ёлочка или новогодний шарик)\n"
            "• 🍫2 шоколадки Kinder\n"
            "• 🍭Леденец\n"
            "• 🎄Новогодний шарик\n"
            "• ❄️Искусственный снег, мишура и праздничная коробка"
        ),
        "image_path": "images/set_1.jpg"
    },
    "set_2": {
        "name": "Тёплый снег",
        "price": 1500,
        "description": (
            "«Тёплый снег ❄️» (1500 руб):\n"
            "• 🏠Набор для создания пряничного домика\n"
            "• 🥮Имбирный человечек\n"
            "• 🍫4 шоколадки Kinder\n"
            "• 🍭Зелёный леденец\n"
            "• 🎄Красный новогодний шарик\n"
            "• ❄️Искусственный снег, мишура и праздничная коробка"
        ),
        "image_path": "images/set_2.jpg"
    },
    "set_3": {
        "name": "Семейное волшебство",
        "price": 2000,
        "description": (
            "«Семейное волшебство 🪄» (2000 руб):\n"
            "• 🏠Набор для создания пряничного домика\n"
            "• 🥮3 имбирных человечка\n"
            "• 🍫6 шоколадок Kinder\n"
            "• 🍭2 зелёных леденца\n"
            "• 🎄2 красных новогодних шарика\n"
            "• ❄️Искусственный снег, мишура и праздничная коробка"
        ),
        "image_path": "images/set_3.jpg"
    }
}


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "🎄 Приветствую и с наступающими праздниками! Здесь вы можете:\n"
        "- Узнать подробнее о наших новогодних наборах\n"
        "- Задать любой вопрос\n"
        "- Оформить предзаказ и порадовать себя или близких!\n\n"
        "Начнем с главного, Вы проживаете в Казани?",
        reply_markup=town_answers
    )


@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    # Главное меню
    if data == "main_menu":
        await callback.message.edit_text(
            "Прекрасно! Итак, что вас интересует?",
            reply_markup=main_menu_kb
        )
    elif data =='no_variant':
        await callback.message.edit_text(
            "К сожалению, наш санта пока летает только по Казани :)"
        )

    elif data == "details":
        await callback.message.edit_text(
            "Супер! О каком наборе вы бы хотели узнать подробнее?",
            reply_markup=sets_menu_kb
        )

    elif data == "other_question":
        # Пользователь хочет задать вопрос
        await callback.message.edit_text(
            "Отлично! Напишите ваш вопрос, и я передам его нашему помощнику🎅 "
            "Он свяжется с вами в ближайшее время.\n\nКогда будете готовы задать вопрос, просто напишите его сообщением.",
            reply_markup=other_question_kb
        )
        await state.set_state(QuestionStates.waiting_for_question)

    elif data == "preorder":
        # Оформить предзаказ – сначала покажем наборы
        await callback.message.edit_text(
            "Прекрасно🎁! Какой набор вы выбрали?",
            reply_markup=sets_menu_kb
        )

    elif data == "back_to_main":
        await state.clear()
        await callback.message.edit_text(
            "Что вы хотите выбрать?",
            reply_markup=main_menu_kb
        )

    elif data in ["set_1", "set_2", "set_3"]:
        await state.update_data(chosen_set=data)
        set_info = sets_data[data]
        # Удаляем текущее сообщение (текстовое)
        await callback.message.delete()
        # Отправляем новое сообщение с фото и описанием
        photo = FSInputFile(set_info['image_path'])
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo,
            caption=set_info['description'],
            reply_markup=set_detail_kb()
        )

    elif data == "back_to_sets":
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="Супер! О каком наборе вы бы хотели узнать подробнее?",
            reply_markup=sets_menu_kb
        )

    elif data == "order":
        # Оформить заказ для выбранного набора
        user_data = await state.get_data()
        chosen_set_key = user_data.get("chosen_set")
        if not chosen_set_key:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")
            return
        set_info = sets_data[chosen_set_key]

        # Удаляем фото-сообщение перед показом следующего шага
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=(
                "Отлично! Уже можно чувствовать нотки Нового года в воздухе🎄!\n\n"
                "Чтобы оформить предзаказ, нужно будет оплатить 50% от стоимости.\n\n"
                f"Вы выбрали набор «{set_info['name']}» стоимостью {set_info['price']} руб.\n\n"
                "После оплаты напишите ваше имя и дату, к которой вы будете готовы забрать этот набор.\n\n"
                "Готовы оформить заказ🎁?"
            ),
            reply_markup=order_confirm_kb
        )

    elif data == "order_think_again":
        # Вернуться к описанию набора
        user_data = await state.get_data()
        chosen_set = user_data.get("chosen_set", None)
        if chosen_set:
            set_info = sets_data[chosen_set]
            await callback.message.delete()
            photo = FSInputFile(set_info['image_path'])
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=photo,
                caption=set_info['description'],
                reply_markup=set_detail_kb()
            )
        else:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")

    elif data == "order_yes":
        # Переход в состояние ожидания ввода данных по заказу
        user_data = await state.get_data()
        chosen_set_key = user_data.get("chosen_set", None)
        if chosen_set_key is None:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")
            return
        set_info = sets_data[chosen_set_key]

        # Удаляем текущее (текстовое) сообщение и отправляем новое
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=(
                f"Ура! Вы выбрали набор «{set_info['name']}» за {set_info['price']} руб.\n\n"
                "Теперь, пожалуйста, напишите свое имя и дату, к которой вы будете готовы забрать этот набор🔔\n\n"
                "После этого я передам информацию нашему помощнику, и он свяжется с вами!\n\n"
            ),
            reply_markup=after_order_main_menu_kb
        )
        await state.set_state(OrderStates.waiting_for_order_info)


@dp.message(OrderStates.waiting_for_order_info)
async def handle_order_info(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_set_key = user_data.get("chosen_set", "неизвестный набор")
    chosen_set = sets_data.get(chosen_set_key, {"name": "Неизвестно", "price": "неизвестна"})

    user_text = message.text
    username = message.from_user.username
    user_id = message.from_user.id

    admin_text = (
        f"Новый предзаказ!\n\n"
        f"Имя/Дата: {user_text}\n"
        f"Набор: {chosen_set['name']} (Цена: {chosen_set['price']} руб)\n"
        f"Username: @{username if username else 'нет юзернейма'}\n"
        f"User ID: {user_id}\n"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
    await message.answer("Отлично! Ваши данные отправлены нашему помощнику. Ожидайте ответа. 🎅")
    await state.clear()


@dp.message(QuestionStates.waiting_for_question)
async def handle_user_question(message: Message, state: FSMContext):
    # Пользователь задал вопрос
    question_text = message.text
    username = message.from_user.username
    user_id = message.from_user.id

    admin_text = (
        f"Вам поступил новый вопрос!\n\n"
        f"Текст вопроса: {question_text}\n"
        f"Username: @{username if username else 'нет юзернейма'}\n"
        f"User ID: {user_id}\n\n"
        "Ответьте командой вида:\n"
        "/answer USER_ID Ваш ответ"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
    await message.answer("Ваш вопрос отправлен нашему помощнику! Он свяжется с вами в ближайшее время.")
    await state.clear()


@dp.message(Command("answer"))
async def admin_answer(message: Message, command: CommandObject):
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        return  # Только админ может использовать эту команду

    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Неверный формат команды. Используйте /answer USER_ID Текст ответа")
        return

    user_id = args[1]
    answer_text = args[2]

    try:
        user_id_int = int(user_id)
    except ValueError:
        await message.answer("User ID должен быть числом.")
        return

    await bot.send_message(chat_id=user_id_int, text=f"Ответ от помощника:\n\n{answer_text}")
    await message.answer("Ответ отправлен пользователю.")


# ----------- Заглушки для Render -----------
async def handle(request):
    return web.Response(text="Бот работает!")

async def keep_alive():
    while True:
        try:
            await bot.get_me()
            print("Бот активен, соединение поддерживается")
        except Exception as e:
            print(f"Ошибка поддержания соединения: {e}")
        await asyncio.sleep(600)

async def start_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

async def main():
    print("Бот запущен...")
    loop = asyncio.get_event_loop()
    loop.create_task(keep_alive())
    loop.create_task(start_server())  # Запуск заглушки для Render
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
