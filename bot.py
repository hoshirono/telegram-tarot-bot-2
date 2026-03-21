import asyncio
import random
import os
import json

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 📁 файл коллекции
COLLECTION_FILE = "collection.json"

# 🎮 кнопки
kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔮 Получить карту")],
        [KeyboardButton(text="📦 Моя коллекция")]
    ],
    resize_keyboard=True
)

# 🎨 стили
STYLES = [
    "dark tarot",
    "cute anime tarot",
    "absurd meme tarot",
    "psychedelic cursed tarot",
    "low quality meme tarot"
]

# 💎 редкость (с шансами)
def get_rarity():
    roll = random.randint(1, 100)
    if roll <= 70:
        return ("обычная карта", "soft tarot")
    elif roll <= 95:
        return ("редкая карта", "glowing detailed tarot")
    else:
        return ("ПРОКЛЯТАЯ 😈", "horror cursed demonic tarot")

# 🃏 названия карт
CARDS = [
    "Сигма Жабий Император",
    "Плачущий Хлеб",
    "Демон Wi-Fi",
    "Картофель Судьбы",
    "Кот с налогами",
    "Гигачад Пророк",
    "Проклятый Хомяк",
    "Скелет на зарплате",
    "Пельмень Вечности"
]

# 🧠 предсказания (абсурд)
PREDICTIONS = [
    "Ты скоро найдешь деньги… но это будет 47 рублей и чек из магнита.",
    "Судьба говорит: иди спать, ты уже натворил достаточно.",
    "Кто-то думает о тебе. Возможно налоговая.",
    "Ты избран… но для чего — никто не знает.",
    "Не доверяй человеку с энергетиком в 3 ночи.",
    "Скоро произойдет херня. Будь готов.",
    "Ты на правильном пути. Просто путь — говно.",
    "В твоей жизни появится кот. Или проблема. Или оба.",
    "Судьба шепчет: 'ну ты и долбоеб конечно'",
    "Ты станешь легендой… в очень узком кругу людей."
]

# 🎨 генерация картинки
def generate_image(style, rarity, card_name):
    prompt = f"{style}, {rarity}, tarot card of {card_name}, absurd, detailed, mystical"
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# 💾 загрузка коллекции
def load_collection():
    if not os.path.exists(COLLECTION_FILE):
        return {}
    with open(COLLECTION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 💾 сохранение
def save_collection(data):
    with open(COLLECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🔮 Добро пожаловать в таро безумия", reply_markup=kb)

# 🔮 получить карту
@dp.message(lambda m: m.text == "🔮 Получить карту")
async def card(message: types.Message):
    await message.answer("🔮 Генерирую карту...")

    style = random.choice(STYLES)
    rarity_text, rarity_prompt = get_rarity()
    card_name = random.choice(CARDS)
    text = random.choice(PREDICTIONS)

    image_url = generate_image(style, rarity_prompt, card_name)

    caption = f"""
🃏 {card_name}

🎨 Стиль: {style}
💎 Редкость: {rarity_text}

🧠 {text}
"""

    try:
        await message.answer_photo(photo=image_url, caption=caption)
    except:
        await message.answer("⚠️ Не удалось загрузить картинку, но вот твоя карта:")
        await message.answer(caption)

    # сохраняем
    user_id = str(message.from_user.id)
    data = load_collection()

    if user_id not in data:
        data[user_id] = []

    data[user_id].append({
        "name": card_name,
        "rarity": rarity_text
    })

    save_collection(data)

# 📦 коллекция
@dp.message(lambda m: m.text == "📦 Моя коллекция")
async def collection(message: types.Message):
    data = load_collection()
    user_id = str(message.from_user.id)

    if user_id not in data or not data[user_id]:
        await message.answer("📭 У тебя пока нет карт")
        return

    text = "📦 Твоя коллекция:\n\n"

    for card in data[user_id][-10:]:
        text += f"🃏 {card['name']} — {card['rarity']}\n"

    await message.answer(text)

# fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми кнопки 👇", reply_markup=kb)

# запуск
async def main():
    print("🚀 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())