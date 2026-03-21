import asyncio
import random
import os
import requests

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile

# 🔑 ключи
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🧠 использованные карты (чтобы не повторялись)
used_cards = set()

# 💎 редкость
RARITY = [
    "обычная",
    "редкая",
    "легендарная",
    "проклятая 😈"
]

# 🎴 пул карт (абсурд + жестко)
CARD_POOL = [
    ("Бог кредитов", "Ты продал душу за рассрочку и даже не заметил."),
    ("Пельмень-оракул", "Твоя судьба кипит в кастрюле, и крышка уже дрожит."),
    ("Wi-Fi демон", "Ты завис между мирами, как слабый сигнал."),
    ("Скелет на удалёнке", "Ты мёртв внутри, но продолжаешь работать."),
    ("Глаз налоговой", "Ты думаешь, что спрятался. Это мило."),
    ("Король кринжа", "Ты стал тем, над кем смеялся."),
    ("404 пророк", "Твоё будущее не найдено."),
    ("Кринжовый ангел", "Даже небеса разочарованы в тебе."),
    ("Шаман подписок", "Ты платишь за то, чем не пользуешься."),
    ("Демон дедлайна", "Он уже здесь. И ты не успеешь."),
]

# 🎴 генерация уникальной карты
def generate_card():
    while True:
        card = random.choice(CARD_POOL)
        if card[0] not in used_cards:
            used_cards.add(card[0])
            return card

# 🎨 генерация картинки (НОВЫЙ API HuggingFace)
def generate_image(name, desc):
    API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    prompt = f"""
Tarot card illustration.

Card title: "{name}"

Scene:
{desc}

Visual requirements:
- surreal absurd scene
- exaggerated emotions
- symbolic composition
- character representing the meaning
- dark humor
- slightly humiliating tone (funny)
- grotesque absurd elements
- cursed meme energy
- detailed tarot card frame
- centered composition
- dramatic lighting
- masterpiece, highly detailed

IMPORTANT:
- image MUST match the meaning
- no random objects
- clear concept
"""

    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "inputs": prompt,
            "options": {"wait_for_model": True}
        },
        timeout=120
    )

    if response.status_code != 200:
        raise Exception(response.text)

    return response.content

# 🎮 клавиатура
def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎰 Крутить")],
            [KeyboardButton(text="📦 Коллекция"), KeyboardButton(text="📊 Стата")]
        ],
        resize_keyboard=True
    )

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 ULTIMATE TAROT\n\nЖми 🎰 Крутить и получи свою судьбу",
        reply_markup=main_keyboard()
    )

# 🎴 генерация карты
@dp.message(lambda m: m.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую карту...")

    name, desc = generate_card()
    rarity = random.choice(RARITY)

    try:
        img_bytes = generate_image(name, desc)
        photo = BufferedInputFile(img_bytes, filename="card.png")

        caption = f"""
🃏 {name}

💎 {rarity}

🔮 {desc}
"""

        await message.answer_photo(photo=photo, caption=caption)

    except Exception as e:
        print("ERROR:", e)
        await message.answer("⚠️ не удалось сгенерировать арт (попробуй ещё раз)")

# 📦 коллекция (пока заглушка)
@dp.message(lambda m: m.text == "📦 Коллекция")
async def collection(message: types.Message):
    if not used_cards:
        await message.answer("У тебя пока нет карт")
    else:
        cards = "\n".join(used_cards)
        await message.answer(f"📦 Твои карты:\n\n{cards}")

# 📊 стата (заглушка)
@dp.message(lambda m: m.text == "📊 Стата")
async def stats(message: types.Message):
    await message.answer(f"📊 Открыто карт: {len(used_cards)}")

# fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми 🎰 Крутить")

# ▶️ запуск
async def main():
    print("Бот запущен 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())