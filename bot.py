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

DB = "data.json"

# ================== БАЗА ==================

def load():
    if not os.path.exists(DB):
        return {}
    with open(DB, "r", encoding="utf-8") as f:
        return json.load(f)

def save(data):
    with open(DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, uid):
    if uid not in data:
        data[uid] = {
            "coins": 500,
            "cards": [],
            "names": [],
            "wins": 0,
            "losses": 0,
            "last_daily": 0
        }
    return data[uid]

# ================== ГЕНЕРАЦИЯ ==================

def rarity_roll():
    r = random.randint(1, 100)
    if r <= 60: return "Обычная", 1
    if r <= 90: return "Редкая", 2
    if r <= 98: return "Легендарная 💀", 3
    return "ПРОКЛЯТАЯ 😈", 5

def gen_name():
    a = ["Император","Жрица","Рыцарь","Дьявол","Маг","Скелет","Кот","Пельмень"]
    b = ["Хаоса","Кринжа","Судьбы","Wi-Fi","Налогов","Абсурда","Боли"]
    return f"{random.choice(a)} {random.choice(b)}"

def gen_text():
    base = [
        "Ты столкнёшься с хаосом",
        "Сегодня будет странно",
        "Ты снова всё испортишь",
        "Судьба уже смеётся",
        "Ты выбрал худший путь"
    ]
    end = [
        "и это нормально",
        "но ты справишься",
        "или нет",
        "никто не знает",
        "смирись"
    ]
    return random.choice(base) + ", " + random.choice(end)

def gen_image(name, rarity, text):
    prompt = f"tarot card, {name}, {rarity}, {text}, surreal, detailed"
    return f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

# ================== UI ==================

def kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Крутить", callback_data="roll")],
        [InlineKeyboardButton(text="⚔️ PvP", callback_data="pvp")],
        [InlineKeyboardButton(text="🧬 Синтез", callback_data="craft")],
        [InlineKeyboardButton(text="📦 Коллекция", callback_data="col")],
        [InlineKeyboardButton(text="📊 Стата", callback_data="stats")],
        [InlineKeyboardButton(text="🎁 Дейлик", callback_data="daily")]
    ])

# ================== СТАРТ ==================

@dp.message(CommandStart())
async def start(m: types.Message):
    data = load()
    get_user(data, str(m.from_user.id))
    save(data)
    await m.answer("💀 ULTIMATE TAROT ONLINE", reply_markup=kb())

# ================== РОЛЛ ==================

@dp.callback_query(lambda c: c.data == "roll")
async def roll(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    if user["coins"] < 100:
        await c.message.answer("💸 Нет монет")
        return

    user["coins"] -= 100

    rarity, power = rarity_roll()

    for _ in range(20):
        name = gen_name()
        if name not in user["names"]:
            break

    text = gen_text()
    img = gen_image(name, rarity, text)

    try:
        await c.message.answer_photo(photo=img, caption=f"🃏 {name}\n💎 {rarity}\n🔮 {text}")
    except:
        await c.message.answer(f"{name}\n{text}")

    user["cards"].append({"name": name, "power": power})
    user["names"].append(name)

    save(data)

# ================== PVP ==================

@dp.callback_query(lambda c: c.data == "pvp")
async def pvp(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    if not user["cards"]:
        await c.message.answer("❌ Нет карт")
        return

    my = random.choice(user["cards"])
    enemy_power = random.randint(1, 5)

    if my["power"] >= enemy_power:
        user["wins"] += 1
        user["coins"] += 150
        result = "🏆 Победа!"
    else:
        user["losses"] += 1
        result = "💀 Поражение"

    save(data)

    await c.message.answer(f"⚔️ Битва\nТвоя карта: {my['name']}\n\n{result}")

# ================== СИНТЕЗ ==================

@dp.callback_query(lambda c: c.data == "craft")
async def craft(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    if len(user["cards"]) < 2:
        await c.message.answer("❌ Нужно 2 карты")
        return

    c1 = user["cards"].pop()
    c2 = user["cards"].pop()

    new_name = c1["name"].split()[0] + " " + c2["name"].split()[1]
    new_power = max(c1["power"], c2["power"]) + 1

    user["cards"].append({"name": new_name, "power": new_power})
    user["names"].append(new_name)

    save(data)

    await c.message.answer(f"🧬 Новая карта: {new_name}")

# ================== ДЕЙЛИК ==================

@dp.callback_query(lambda c: c.data == "daily")
async def daily(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    now = int(time.time())

    if now - user["last_daily"] < 86400:
        await c.message.answer("⏳ Уже было")
        return

    reward = random.randint(100, 300)
    user["coins"] += reward
    user["last_daily"] = now

    save(data)

    await c.message.answer(f"🎁 +{reward} 💰")

# ================== КОЛЛЕКЦИЯ ==================

@dp.callback_query(lambda c: c.data == "col")
async def col(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    if not user["cards"]:
        await c.message.answer("📭 Пусто")
        return

    text = "📦 Коллекция:\n\n"
    for card in user["cards"][-10:]:
        text += f"🃏 {card['name']}\n"

    await c.message.answer(text)

# ================== СТАТА ==================

@dp.callback_query(lambda c: c.data == "stats")
async def stats(c: types.CallbackQuery):
    data = load()
    uid = str(c.from_user.id)
    user = get_user(data, uid)

    await c.message.answer(f"""
📊 Статистика

💰 {user['coins']}
🏆 {user['wins']} побед
💀 {user['losses']} поражений
🃏 {len(user['cards'])} карт
""")

# ================== ЗАПУСК ==================

async def main():
    print("🔥 ULTIMATE BOT RUNNING")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())