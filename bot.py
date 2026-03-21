import asyncio
import random
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ======================
# 🔑 ВСТАВЬ СЮДА
# ======================
TOKEN = "8705289370:AAGPqjd8uNsnyr04zCM0S3pOjo1jLUSW0vg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ======================
# 🧠 ПАМЯТЬ
# ======================
user_memory = {}

# ======================
# 🔘 КНОПКА
# ======================
def get_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💀 Получить судьбу"))
    return kb

# ======================
# 🖼️ ГЕНЕРАЦИЯ ФОТО (БЕЗ API)
# ======================
def get_cursed_image():
    themes = [
        "weird face close up",
        "distorted human body",
        "liminal space empty room",
        "strange creepy object",
        "weird food disgusting",
        "ugly animal close up",
        "blurry shadow figure",
        "abandoned building creepy",
        "strange mannequin",
        "distorted selfie"
    ]
    theme = random.choice(themes)
    return f"https://source.unsplash.com/800x800/?{theme}"

# ======================
# 🔮 ГЕНЕРАЦИЯ ПРЕДСКАЗАНИЯ
# ======================
def generate_prediction(user_text=None):
    insults = [
        "гений без шансов",
        "человек-ошибка",
        "недоразумение с Wi-Fi",
        "случайный баг реальности",
        "побочный квест без награды",
        "живое разочарование"
    ]

    events = [
        "ты опять облажаешься",
        "все пойдет странно и криво",
        "кто-то будет тебя терпеть из жалости",
        "ты снова выберешь худший вариант",
        "вселенная слегка над тобой посмеётся",
        "реальность даст тебе пощёчину"
    ]

    endings = [
        "и ты сделаешь вид что так и было задумано",
        "но ты всё равно ничего не поймёшь",
        "и это будет даже не самый худший исход",
        "но ты опять не сделаешь выводов",
        "и да, это только начало",
        "но ты продолжишь в том же духе"
    ]

    insult = random.choice(insults)
    event = random.choice(events)
    ending = random.choice(endings)

    if user_text:
        return f"Ты писал: '{user_text[:20]}...' — и это многое объясняет.\n\nСегодня ты, {insult}, {event}, {ending}."
    else:
        return f"Сегодня ты, {insult}, {event}, {ending}."

# ======================
# 🚀 СТАРТ
# ======================
@dp.message(lambda msg: msg.text == "/start")
async def start(msg: types.Message):
    await msg.answer(
        "О, ты вернулся. Не знаю зачем, но ладно.\nЖми кнопку и страдай.",
        reply_markup=get_keyboard()
    )

# ======================
# 💀 КНОПКА
# ======================
@dp.message(lambda msg: msg.text == "💀 Получить судьбу")
async def get_fate(msg: types.Message):
    await msg.answer("...смотрю в твою жалкую судьбу...")

    await bot.send_chat_action(msg.chat.id, "typing")
    await asyncio.sleep(2)

    image_url = get_cursed_image()
    memory = user_memory.get(msg.from_user.id)

    text = generate_prediction(memory)

    await msg.answer_photo(photo=image_url, caption=text)

# ======================
# 🧠 ЗАПОМИНАНИЕ
# ======================
@dp.message()
async def remember(msg: types.Message):
    user_memory[msg.from_user.id] = msg.text
    await msg.answer("Запомнил. Зря ты это написал.")

# ======================
# ▶️ ЗАПУСК
# ======================
async def main():
    print("Бот запущен 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())