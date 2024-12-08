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
API_TOKEN = os.getenv('API_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')
DEBUG = os.getenv('DEBUG', 'False')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderStates(StatesGroup):
    waiting_for_order_info = State()
    waiting_for_filling_choice_little = State()    # Маленькое чудо
    waiting_for_filling_choice_snow = State()      # Тёплый снег
    waiting_for_filling_choice_magic_1 = State()   # Семейное волшебство - первый выбор
    waiting_for_filling_choice_magic_2 = State()   # Семейное волшебство - второй выбор

class QuestionStates(StatesGroup):
    waiting_for_question = State()

town_answers = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Да!', callback_data='main_menu')],
        [InlineKeyboardButton(text='Другой город', callback_data='no_variant')]
    ]
)

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1. Подробнее о наборах 🏠", callback_data="details")],
        [InlineKeyboardButton(text="2. Другой вопрос ❓", callback_data="other_question")],
        [InlineKeyboardButton(text="3. Акции ⭐", callback_data="actions")],
        [InlineKeyboardButton(text="4. Оформить предзаказ 🎁", callback_data="preorder")]
    ]
)

sets_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="1. «Маленькое чудо ✨» (1000 руб)", callback_data="set_1")],
        [InlineKeyboardButton(text="2. «Тёплый снег ❄️» (1500 руб)", callback_data="set_2")],
        [InlineKeyboardButton(text="3. «Семейное волшебство 🪄» (2000 руб)", callback_data="set_3")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
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

actions_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Бонус за предзаказ 🎁", callback_data="action_preorder_bonus")],
        [InlineKeyboardButton(text="Подарочная открытка ✨", callback_data="action_card")],
        [InlineKeyboardButton(text="Время-ограниченная акция ⏰", callback_data="action_limited")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_main")]
    ]
)

def action_back_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="actions")]
        ]
    )

# Клавиатуры для выбора
little_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Елочка 🌲", callback_data="little_елочка")],
        [InlineKeyboardButton(text="Новогодний шарик 🎄", callback_data="little_шарик")],
        [InlineKeyboardButton(text="Назад", callback_data="little_back")]
    ]
)

snow_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Example1", callback_data="snow_ex1")],
        [InlineKeyboardButton(text="Example2", callback_data="snow_ex2")],
        [InlineKeyboardButton(text="Назад", callback_data="snow_back")]
    ]
)

magic_first_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Example1", callback_data="magic1_ex1")],
        [InlineKeyboardButton(text="Example2", callback_data="magic1_ex2")],
        [InlineKeyboardButton(text="Назад", callback_data="magic1_back")]
    ]
)

magic_second_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Example1", callback_data="magic2_ex1")],
        [InlineKeyboardButton(text="Example2", callback_data="magic2_ex2")],
        [InlineKeyboardButton(text="Example3", callback_data="magic2_ex3")],
        [InlineKeyboardButton(text="Назад", callback_data="magic2_back")]
    ]
)

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
        "🎄 Приветствую! Здесь вы можете:\n"
        "- Узнать подробнее о наших новогодних наборах\n"
        "- Задать любой вопрос\n"
        "- Узнать об актуальных акциях\n"
        "- Оформить предзаказ и порадовать себя или близких!\n\n"
        "Начнем с главного, Вы проживаете в Казани?",
        reply_markup=town_answers
    )

@dp.callback_query()
async def handle_callbacks(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "main_menu":
        await callback.message.edit_text(
            "Прекрасно! Итак, что вас интересует?",
            reply_markup=main_menu_kb
        )

    elif data == 'no_variant':
        await callback.message.edit_text(
            "К сожалению, наш санта пока летает только по Казани :)"
        )

    elif data == "details":
        await callback.message.edit_text(
            "Супер! О каком наборе вы бы хотели узнать подробнее?",
            reply_markup=sets_menu_kb
        )

    elif data == "other_question":
        await callback.message.edit_text(
            "Отлично! Напишите ваш вопрос, и я передам его нашему помощнику🎅 "
            "Он свяжется с вами в ближайшее время.\n\nКогда будете готовы задать вопрос, просто напишите его сообщением.",
            reply_markup=other_question_kb
        )
        await state.set_state(QuestionStates.waiting_for_question)

    elif data == "actions":
        await callback.message.edit_text(
            "Здесь вы сможете найти и узнать подробнее о наших актуальных акциях⭐",
            reply_markup=actions_menu_kb
        )

    elif data == "action_preorder_bonus":
        await callback.message.edit_text(
            "Бонус за предзаказ 🎁:\n\nЗакажите свой набор до 15 декабря и получите дополнительный имбирный человечек в подарок!",
            reply_markup=action_back_kb()
        )

    elif data == "action_card":
        await callback.message.edit_text(
            "Подарочная открытка ✨:\n\nДо 15 декабря мы можем приложить именную открытку с вашим поздравлением — бесплатно!",
            reply_markup=action_back_kb()
        )

    elif data == "action_limited":
        await callback.message.edit_text(
            "Время-ограниченная акция ⏰:\n\nДо 15 декабря — дополнительная шоколадка Kinder без доплаты!",
            reply_markup=action_back_kb()
        )

    elif data == "preorder":
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
        await callback.message.delete()
        photo_msg = await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=FSInputFile(set_info['image_path']),
            caption=set_info['description'],
            reply_markup=set_detail_kb()
        )
        # Сохраним id основного сообщения с набором
        await state.update_data(photo_messages=[photo_msg.message_id])

    elif data == "back_to_sets":
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="Супер! О каком наборе вы бы хотели узнать подробнее?",
            reply_markup=sets_menu_kb
        )

    elif data == "order":
        user_data = await state.get_data()
        chosen_set_key = user_data.get("chosen_set")
        if not chosen_set_key:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")
            return
        # Удаляем текущее фото и сообщение
        await delete_photo_messages(state, callback)
        await callback.message.delete()

        # Отправляем нужные фото в зависимости от набора
        photo_ids = []

        if chosen_set_key == "set_1":
            # Маленькое чудо: 1 фотка example_1
            msg1 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/choice_tree.jpg"))
            photo_ids.append(msg1.message_id)
            await state.update_data(photo_messages=photo_ids)
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Какое наполнение вы желаете?",
                reply_markup=little_choice_kb
            )
            await state.set_state(OrderStates.waiting_for_filling_choice_little)

        elif chosen_set_key == "set_2":
            # Тёплый снег: 2 фотки example_2 и example_3
            msg1 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_1.jpg"))
            msg2 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_2.jpg"))
            photo_ids.extend([msg1.message_id, msg2.message_id])
            await state.update_data(photo_messages=photo_ids)
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Какое наполнение вы желаете?",
                reply_markup=snow_choice_kb
            )
            await state.set_state(OrderStates.waiting_for_filling_choice_snow)

        elif chosen_set_key == "set_3":
            # Семейное волшебство: первый выбор - example_2 и example_3
            msg1 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_1.jpg"))
            msg2 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_2.jpg"))
            photo_ids.extend([msg1.message_id, msg2.message_id])
            await state.update_data(photo_messages=photo_ids)
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Какое наполнение вы желаете? (первый выбор)",
                reply_markup=magic_first_choice_kb
            )
            await state.set_state(OrderStates.waiting_for_filling_choice_magic_1)

    elif data == "order_think_again":
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        user_data = await state.get_data()
        chosen_set = user_data.get("chosen_set", None)
        if chosen_set:
            set_info = sets_data[chosen_set]
            msg = await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=FSInputFile(set_info['image_path']),
                caption=set_info['description'],
                reply_markup=set_detail_kb()
            )
            await state.update_data(photo_messages=[msg.message_id])
        else:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")

    # Обработка для "Маленькое чудо"
    elif data in ["little_елочка", "little_шарик", "little_back"]:
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        if data == "little_back":
            # Назад к описанию набора
            user_data = await state.get_data()
            chosen_set_key = user_data.get("chosen_set")
            set_info = sets_data[chosen_set_key]
            msg = await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=FSInputFile(set_info['image_path']),
                caption=set_info['description'],
                reply_markup=set_detail_kb()
            )
            await state.update_data(photo_messages=[msg.message_id])
            await state.clear_state(OrderStates.waiting_for_filling_choice_little)
        else:
            # Выбран вариант
            await state.update_data(filling=data.replace("little_", ""))
            await send_booking_options(callback, state)

    # Обработка для "Тёплый снег"
    elif data in ["snow_ex1", "snow_ex2", "snow_back"]:
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        if data == "snow_back":
            user_data = await state.get_data()
            chosen_set_key = user_data.get("chosen_set")
            set_info = sets_data[chosen_set_key]
            msg = await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=FSInputFile(set_info['image_path']),
                caption=set_info['description'],
                reply_markup=set_detail_kb()
            )
            await state.update_data(photo_messages=[msg.message_id])
            await state.clear_state(OrderStates.waiting_for_filling_choice_snow)
        else:
            await state.update_data(snow_choice=data.replace("snow_", ""))
            await send_booking_options(callback, state)

    # Семейное волшебство - первый выбор
    elif data in ["magic1_ex1", "magic1_ex2", "magic1_back"]:
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        if data == "magic1_back":
            user_data = await state.get_data()
            chosen_set_key = user_data.get("chosen_set")
            set_info = sets_data[chosen_set_key]
            msg = await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=FSInputFile(set_info['image_path']),
                caption=set_info['description'],
                reply_markup=set_detail_kb()
            )
            await state.update_data(photo_messages=[msg.message_id])
            await state.clear_state(OrderStates.waiting_for_filling_choice_magic_1)
        else:
            await state.update_data(magic_choice_1=data.replace("magic1_", ""))
            # Теперь второй выбор: перед ним тоже нужно показать 2 фотки (example_4 и example_1)
            # Отправим новые фото
            msg1 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/choice_cookies.jpg"))
            msg2 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/choice_tree.jpg"))
            await state.update_data(photo_messages=[msg1.message_id, msg2.message_id])
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Какой второй вариант вы желаете?",
                reply_markup=magic_second_choice_kb
            )
            await state.set_state(OrderStates.waiting_for_filling_choice_magic_2)

    # Семейное волшебство - второй выбор
    elif data in ["magic2_ex1", "magic2_ex2", "magic2_ex3", "magic2_back"]:
        await delete_photo_messages(state, callback)
        await callback.message.delete()
        if data == "magic2_back":
            # Вернуться к первому выбору
            # Снова отправим example_2 и example_3
            msg1 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_1.jpg"))
            msg2 = await bot.send_photo(chat_id=callback.message.chat.id, photo=FSInputFile("images/home_2.jpg"))
            await state.update_data(photo_messages=[msg1.message_id, msg2.message_id])
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text="Какое наполнение вы желаете? (первый выбор)",
                reply_markup=magic_first_choice_kb
            )
            await state.set_state(OrderStates.waiting_for_filling_choice_magic_1)
        else:
            await state.update_data(magic_choice_2=data.replace("magic2_", ""))
            await send_booking_options(callback, state)

    elif data == "order_yes":
        user_data = await state.get_data()
        chosen_set_key = user_data.get("chosen_set", None)
        if chosen_set_key is None:
            await callback.message.answer("Произошла ошибка, попробуйте ещё раз.")
            return
        await callback.message.delete()
        set_info = sets_data[chosen_set_key]
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text=(
                f"Замечательно! Ваш набор «{set_info['name']}» за {set_info['price']} руб.\n\n"
                "Теперь, пожалуйста, напишите свое имя и дату, к которой вы будете готовы забрать этот набор🔔(в одном сообщении)\n\n"
                "После этого я передам информацию нашему помощнику, и он свяжется с вами!\n\n"
            ),
            reply_markup=after_order_main_menu_kb
        )
        await state.set_state(OrderStates.waiting_for_order_info)

async def send_booking_options(callback: CallbackQuery, state: FSMContext):
    await delete_photo_messages(state, callback)
    await callback.message.delete()
    user_data = await state.get_data()
    chosen_set_key = user_data.get("chosen_set")
    set_info = sets_data[chosen_set_key]

    msg = await bot.send_message(
        chat_id=callback.message.chat.id,
        text=(
            "Отлично! Уже можно чувствовать нотки Нового года в воздухе🎄!\n\n"
            f"Вы выбрали набор «{set_info['name']}» стоимостью {set_info['price']} руб.\n\n"
            "Итак, способы бронирования:\n\n"
            "1. Оплата полностью при получении, если вы заберете набор самовывозом в течении 2-ух дней после заказа(с адреса Николая ершова 62в)\n\n"
            "2. Оформить предзаказ, для этого нужно будет оплатить 50% от стоимости. Для этого с Вами свяжется наш тайный санта!\n\n"
            "Готовы оформить заказ🎁?"
        ),
        reply_markup=order_confirm_kb
    )
    # Здесь больше фото не отправляем, значит messages_photo пусты

async def delete_photo_messages(state: FSMContext, callback: CallbackQuery):
    user_data = await state.get_data()
    photo_messages = user_data.get("photo_messages", [])
    for pmid in photo_messages:
        try:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=pmid)
        except:
            pass
    # Очищаем список фото
    await state.update_data(photo_messages=[])

@dp.message(OrderStates.waiting_for_order_info)
async def handle_order_info(message: Message, state: FSMContext):
    user_data = await state.get_data()
    chosen_set_key = user_data.get("chosen_set", "неизвестный набор")
    chosen_set = sets_data.get(chosen_set_key, {"name": "Неизвестно", "price": "неизвестна"})

    filling_info = ""
    if chosen_set_key == "set_1":
        filling_info = user_data.get("filling", "не выбрано")
    elif chosen_set_key == "set_2":
        filling_info = user_data.get("snow_choice", "не выбрано")
    elif chosen_set_key == "set_3":
        magic_choice_1 = user_data.get("magic_choice_1", "не выбрано")
        magic_choice_2 = user_data.get("magic_choice_2", "не выбрано")
        filling_info = f"Выбор 1: {magic_choice_1}, Выбор 2: {magic_choice_2}"

    user_text = message.text
    username = message.from_user.username
    user_id = message.from_user.id

    admin_text = (
        f"Новый предзаказ!\n\n"
        f"Имя/Дата: {user_text}\n"
        f"Набор: {chosen_set['name']} (Цена: {chosen_set['price']} руб)\n"
        f"Выборы: {filling_info}\n"
        f"Username: @{username if username else 'нет юзернейма'}\n"
        f"User ID: {user_id}\n"
    )

    await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_text)
    await message.answer("Отлично! Ваши данные отправлены нашему помощнику. Ожидайте ответа. 🎅")
    await state.clear()

@dp.message(QuestionStates.waiting_for_question)
async def handle_user_question(message: Message, state: FSMContext):
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
        return

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
    loop.create_task(start_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
