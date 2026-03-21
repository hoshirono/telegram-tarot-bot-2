import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "ТВОЙ_TELEGRAM_TOKEN"
HF_TOKEN = "ТВОЙ_HUGGINGFACE_TOKEN"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🧠 память чтобы не повторялось
used_cards = set()

# 💀 база карт (можешь расширять)
CARDS = [
    "Бомж-Киборг",
    "Wi-Fi Демон",
    "Кредитный Бог",
    "Пельмень Судьбы",
    "Скелет Менеджер",
    "Проклятый Курьер",
    "Дед с RTX",
    "Сломанный Ангел",
    "Бог Микрозаймов",
    "Токсичный Голубь",
    "Грустный Клоун",
    "Глючный Архангел",
    "404 Пророк",
    "Сонный Дракон",
    "Ленивый Некромант",
    "Шаурма Оракул",
]

# 🎨 стили
STYLES = [
    "dark gothic tarot",
    "absurd surreal meme tarot",
    "cyberpunk cursed tarot",
    "hyper detailed fantasy tarot",
    "glitchcore nightmare tarot"
]

# 💎 редкость
RARITY = [
    "обычная",
    "редкая",
    "легендарная",
    "проклятая",
    "запрещённая"
]

# 💀 генерация максимально кринж предсказаний
def generate_text(card):
    phrases = [
        "ты облажался ещё до того как начал",
        "судьба смеётся над тобой в прямом эфире",
        "вселенная дала тебе шанс — и ты его проебал",
        "тебя ждёт успех, но не твой",
        "ты выбрал худший вариант из всех возможных",
        "даже этот бот в тебя не верит",
        "ты буквально статистическая ошибка",
        "твоя жизнь — это побочный квест без награды",
        "ты NPC в чужой истории",
        "система уже списала тебя со счетов"
    ]

    return f"{random.choice(phrases)}."

# 🎨 генерация картинки (НОВЫЙ API)
def generate_image(card, style):
    prompt = f"""
tarot card, {card},
{style},
highly detailed,
center composition,
ornate frame,
mystical symbols,
4k, beautiful, professional art
"""

    try:
        response = requests.post(
            "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0",
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={"inputs": prompt},
            timeout=60
        )

        if response.status_code == 200:
            return response.content
        else:
            print("HF ERROR:", response.text)
            return None

    except Exception as e:
        print("IMAGE ERROR:", e)
        return None

# 🎛 меню
def get_menu():
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎰 Крутить")],
        ],
        resize_keyboard=True
    )
    return kb

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "💀 CRINGE TAROT\nЖми кнопку и страдай",
        reply_markup=get_menu()
    )

# 🎴 генерация карты
@dp.message(lambda msg: msg.text == "🎰 Крутить")
async def spin(message: types.Message):
    await message.answer("🎨 Генерирую максимально кринж карту...")

    # уникальность
    available = list(set(CARDS) - used_cards)

    if not available:
        used_cards.clear()
        available = CARDS.copy()

    card = random.choice(available)
    used_cards.add(card)

    style = random.choice(STYLES)
    rarity = random.choice(RARITY)
    text = generate_text(card)

    caption = f"""
💀 {card}

💎 Редкость: {rarity}

🔮 {text}
"""

    img = generate_image(card, style)

    if img:
        await message.answer_photo(photo=img, caption=caption)
    else:
        await message.answer(f"{caption}\n\n⚠️ арт не сгенерился")

# ▶️ запуск
async def main():
    print("Бот жив 💀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())