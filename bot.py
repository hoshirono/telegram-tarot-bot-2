import asyncio
import random
import os
import json
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "data.json"

# 💾 база
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 🎰 редкость
def roll_rarity():
    r = random.randint(1, 100)
    if r <= 60:
        return "Обычная", "simple"
    elif r <= 90:
        return "Редкая", "detailed glowing"
    elif r <= 98:
        return "Легендарная 💀", "epic cinematic"
    else:
        return "ПРОКЛЯТАЯ 😈", "horror cursed demonic"

# 🃏 генерация уникальной карты
def generate_card_name():
    parts1 = ["Император", "Жрица", "Рыцарь", "Дьявол", "Маг", "Скелет", "Кот", "Пельмень"]
    parts2 = ["Хаоса", "Кринжа", "Судьбы", "Прокрастинации", "Wi-Fi", "Налогов", "Абсурда"]

    return f"{random.choice(parts1)} {random.choice(parts2)}"

# 🧠 уникальное предсказание
def generate_prediction():
    templates = [
        "Ты столкнёшься с {event}, и это изменит всё.",
        "Сегодня судьба принесёт {event}. Готовься.",
        "Твоя жизнь скоро пересечётся с {event}.",
        "Избегай {event}, если хочешь выжить морально.",
        "Ты сам и есть {event}."
    ]

    events = [
        "абсурдным выбором",
        "кринжовой ситуацией",
        "неожиданным позором",
        "глупым решением",
        "хаотичным событием"
    ]

    text = random.choice(templates).format(event=random.choice(events))

    # добавляем немного безумия
    endings = [
        "И да, это будет странно.",
        "Ты не готов.",
        "Но ты всё равно туда полезешь.",
        "Судьба уже смеётся.",
        "Прими это."
    ]

    return text + " " + random.choice(endings)

# 🎨 генерация картинки
def generate_image_url(card_name, rarity_prompt, prediction):
    prompt = f"tarot card, {card_name}, {rarity_prompt}, {prediction}, mystical, detailed, surreal"
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# 🎮 клавиатура
def kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Крутить (100💰)", callback_data="roll")],
        [InlineKeyboardButton(text="🎁 Ежедневка", callback_data="daily")],
        [InlineKeyboardButton(text="📦 Коллекция", callback_data="collection")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])

# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    data = load_data()
    uid = str(message.from_user.id)

    if uid not in data:
        data[uid] = {
            "coins": 500,
            "cards": [],
            "names": [],
            "count": 0,
            "last_daily": 0
        }
        save_data(data)

    await message.answer("💀 ФИНАЛЬНОЕ ТАРО АКТИВНО", reply_markup=kb())

# 🎰 крутка
@dp.callback_query(lambda c: c.data == "roll")
async def roll(callback: types.CallbackQuery):
    data = load_data()
    uid = str(callback.from_user.id)

    if data[uid]["coins"] < 100:
        await callback.message.answer("💸 Нет денег")
        return

    data[uid]["coins"] -= 100

    rarity_text, rarity_prompt = roll_rarity()

    # 🔥 уникальная карта
    for _ in range(20):
        card_name = generate_card_name()
        if card_name not in data[uid]["names"]:
            break

    prediction = generate_prediction()
    image_url = generate_image_url(card_name, rarity_prompt, prediction)

    caption = f"""
🃏 {card_name}
💎 {rarity_text}

🔮 {prediction}
"""

    try:
        await asyncio.wait_for(
            callback.message.answer_photo(photo=image_url, caption=caption),
            timeout=10
        )
    except:
        await callback.message.answer(caption)

    # сохраняем
    data[uid]["cards"].append({
        "name": card_name,
        "rarity": rarity_text,
        "text": prediction
    })
    data[uid]["names"].append(card_name)
    data[uid]["count"] += 1

    save_data(data)

# 🎁 ежедневка
@dp.callback_query(lambda c: c.data == "daily")
async def daily(callback):
    data = load_data()
    uid = str(callback.from_user.id)

    now = int(time.time())

    if now - data[uid]["last_daily"] < 86400:
        await callback.message.answer("⏳ Уже забрал")
        return

    reward = random.randint(150, 400)
    data[uid]["coins"] += reward
    data[uid]["last_daily"] = now

    save_data(data)

    await callback.message.answer(f"🎁 +{reward} 💰")

# 📦 коллекция
@dp.callback_query(lambda c: c.data == "collection")
async def collection(callback):
    data = load_data()
    uid = str(callback.from_user.id)

    cards = data[uid]["cards"]

    if not cards:
        await callback.message.answer("📭 Пусто")
        return

    text = "📦 Коллекция:\n\n"
    for c in cards[-10:]:
        text += f"🃏 {c['name']} — {c['rarity']}\n"

    await callback.message.answer(text)

# 📊 статистика
@dp.callback_query(lambda c: c.data == "stats")
async def stats(callback):
    data = load_data()
    uid = str(callback.from_user.id)

    user = data[uid]

    await callback.message.answer(f"""
📊 Статистика:

💰 Монеты: {user['coins']}
🎰 Крутки: {user['count']}
🃏 Уникальных карт: {len(user['names'])}
""")

# запуск
async def main():
    print("🔥 FINAL BOT RUNNING")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())