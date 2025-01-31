import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random
import json
import os
from aiogram.utils.markdown import hbold

TOKEN = "7752950131:AAH_UHAOt26NgdyIdslp8s7Bd-cnIk0BBPo"



TOKEN_FILE = "tokens.json"


def load_tokens():
    """
    Загружает сохранённые токены из файла JSON.
    Возвращает словарь вида: { "user_id": token, ... }.
    Если файл не найден, возвращает пустой словарь.
    """
    if not os.path.exists(TOKEN_FILE):
        return {}  # Файл отсутствует

    with open(TOKEN_FILE, "r", encoding="utf-8") as file:
        try:
            tokens = json.load(file)
            # В файле мы храним user_id в виде строк, поэтому вернём как есть
            return tokens
        except json.JSONDecodeError:
            return {}  # Файл пустой или повреждён


def save_tokens(tokens):
    """
    Сохраняет словарь токенов в файл JSON.
    """
    with open(TOKEN_FILE, "w", encoding="utf-8") as file:
        json.dump(tokens, file, ensure_ascii=False, indent=4)


def get_user_token(user_id):
    """
    Возвращает токен пользователя, если он уже есть.
    Иначе генерирует новый, сохраняет и возвращает его.

    user_id (int) -> token (int).
    """
    tokens = load_tokens()

    # Приводим user_id к строке, чтобы не было конфликтов при сохранении в JSON
    str_user_id = str(user_id)

    # Если пользователя нет в словаре, генерируем ему токен
    if str_user_id not in tokens:
        new_token = random.randint(1000, 9999)  # Случайное 4-значное число
        tokens[str_user_id] = new_token
        save_tokens(tokens)  # Сохраняем обновлённый словарь

    # Возвращаем токен (тут уже точно есть)
    return tokens[str_user_id]


# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создаем клавиатуру
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🔥 Учавствовать в розыгрыше!")], [KeyboardButton(text="🔥 Узнать информацию про ДОД")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def welcome_user(message: Message):
    await message.answer(
        f"Привет! Я бот Дня открытых дверей ИФТЭБ НИЯУ МИФИ🔥.\n\n"
        "Чтобы получить уникальный токен для участия в розыгрыше ИФТЭБ НИЯУ МИФИ или узнать информацию про День открытых дверей, нажми на кнопки ниже 👇",
        reply_markup=start_keyboard
    )


@dp.message(F.text == "🔥 Узнать информацию про ДОД")
async def start_action(message: Message):
    await message.answer("День открытых дверей НИЯУ МИФИ состоится 9 февраля в студенческом офисе НИЯУ МИФИ. \nНачало в 10:00 \n\n С собой обязательно иметь паспорт. ")

keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться", url=f"https://t.me/iftes_mephi")], [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subscription")]
    ]
)


@dp.message(F.text == "🔥 Учавствовать в розыгрыше!")
async def participate_in_raffle(message: Message):
    user_id = message.from_user.id

    # Проверяем подписку на канал
    chat_member = await bot.get_chat_member(chat_id='@iftes_mephi', user_id=user_id)

    # Если пользователь не подписан
    if chat_member.status not in ["member", "administrator", "creator"]:
        await message.answer(
            "Чтобы участвовать в розыгрыше, нужно подписаться на наш канал. Пожалуйста, сделай это.",
            reply_markup=keyboard
        )
        return

    # Если подписан, выдаем уникальный токен
    unique_token = f"Ваш уникальный токен: {get_user_token(user_id)}"

    await message.answer(f"Поздравляю, вы подписаны на канал! Вот ваш уникальный токен: {unique_token}")

@dp.callback_query(F.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # Проверяем повторно
    chat_member = await bot.get_chat_member(chat_id='@iftes_mephi', user_id=user_id)

    if chat_member.status in ["member", "administrator", "creator"]:
        unique_token = get_user_token(user_id)


        await callback.message.edit_text(f"✅ Спасибо за подписку! Вот ваш уникальный токен: {unique_token}")
    else:
        await callback.answer("Вы еще не подписаны! Подпишитесь и попробуйте снова.", show_alert=True)
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
