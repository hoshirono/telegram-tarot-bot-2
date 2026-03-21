import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

TOKEN = "ТВОЙ_ТОКЕН_СЮДА"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- КНОПКА ---
def get_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔮 Дай мне судьбу, ублюдок")]
        ],
        resize_keyboard=True
    )
    return keyboard


# --- ПРЕДСКАЗАНИЯ ---
def generate_prediction():
    starts = [
        "Сегодня",
        "В ближайшее время",
        "Судя по всему",
        "Очевидно",
        "Ты даже не заметишь как"
    ]

    events = [
        "твоя жизнь снова пойдет по пизде",
        "ты облажаешься в самом простом",
        "все пойдет не так, как ты думаешь",
        "ты будешь выглядеть максимально глупо",
        "вселенная снова над тобой поржет"
    ]

    endings = [
        "и ты ничего с этим не сделаешь",
        "как обычно",
        "потому что ты — это ты",
        "и это уже закономерность",
        "но ты сделаешь вид, что все нормально"
    ]

    return f"{random.choice(starts)} {random.choice(events)}, {random.choice(endings)}."


# --- ФОТО (работает ВСЕГДА) ---
def get_photo():
    # источник, который не ломается
    return f"https://picsum.photos/seed/{random.randint(1,100000)}/600/600"


# --- СТАРТ ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Ну привет. Жми кнопку и получай свою порцию правды.",
        reply_markup=get_keyboard()
    )


# --- КНОПКА ---
@dp.message(lambda message: message.text == "🔮 Дай мне судьбу, ублюдок")
async def tarot(message: types.Message):
    await message.answer_chat_action("typing")

    text = generate_prediction()
    photo = get_photo()

    try:
        await message.answer_photo(
            photo=photo,
            caption=text
        )
    except Exception as e:
        print("Ошибка отправки фото:", e)
        await message.answer(text)


# --- ЛЮБОЙ ТЕКСТ ---
@dp.message()
async def user_text(message: types.Message):
    await message.answer(
        f"Ты написал: {message.text}\n\nЗапомнил. Потом припомню 🙂",
        reply_markup=get_keyboard()
    )


# --- ЗАПУСК ---
async def main():
    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())