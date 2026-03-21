import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔑 токен
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 🎨 стили
STYLES = [
    "dark gothic tarot",
    "cute anime tarot",
    "absurd meme tarot",
    "psychedelic cursed tarot",
    "low budget cursed png tarot",
]

# 💎 редкость
RARITY = [
    ("обычная карта", "common"),
    ("редкая карта", "rare"),
    ("легендарная 💀", "legendary"),
    ("проклятая 😈", "cursed"),
]

# 🃏 абсурдные карты
CARDS = [
    "Король Сломанных Wi-Fi",
    "Туз Кринжа",
    "Жрица Неловкого Молчания",
    "Рыцарь Просроченных Дедлайнов",
    "Дьявол Лени",
    "Колесо Непонятно Чего",
    "Башня, которая просто упала",
    "Император Без Штанов",
    "Маг Потерянных Носков",
    "Смерть, но ты уже привык",
]

# 🧠 ЖЕСТКИЕ ПРЕДСКАЗАНИЯ
PREDICTIONS = [
    "Сегодня ты снова обосрёшься, но уже морально.",
    "Вселенная намекает: пора перестать быть долбоёбом.",
    "Ты на верном пути... но путь ведёт в жопу.",
    "Скоро будет шанс — и ты его, конечно, просрёшь.",
    "Твоя удача: 1/10, но зато стабильно.",
    "Сегодня можно всё. Даже позориться.",
    "Карта говорит: хватит страдать хуйнёй.",
    "Ты главный герой… но комедии.",
    "Всё будет нормально. Наверное. Нет.",
    "Ты думаешь это знак? Да. Плохой.",
]

# 📚 коллекция пользователей
user_cards = {}


# 🔘 клавиатура
def get_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔮 Получить карту", callback_data="card")],
        [InlineKeyboardButton(text="📚 Моя коллекция", callback_data="collection")]
    ])
    return kb


# 🚀 старт
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "🔮 Добро пожаловать в самый ебанутый таро-бот\n\nЖми кнопку 👇",
        reply_markup=get_keyboard()
    )


# 🎴 генерация карты
async def generate_card():
    await asyncio.sleep(1)  # имитация генерации

    style = random.choice(STYLES)
    rarity_text, _ = random.choice(RARITY)
    card_name = random.choice(CARDS)
    prediction = random.choice(PREDICTIONS)

    # 🖼️ простые картинки (чтобы не зависало)
    images = [
        "https://picsum.photos/400/600",
        "https://placekitten.com/400/600",
        "https://placebear.com/400/600"
    ]

    image = random.choice(images)

    caption = f"""
🃏 {card_name}

🎨 Стиль: {style}
💎 Редкость: {rarity_text}

🔮 {prediction}
"""

    return image, caption, card_name


# 🎴 кнопка "получить карту"
@dp.callback_query(lambda c: c.data == "card")
async def card_callback(callback: types.CallbackQuery):
    await callback.message.answer("🔮 Генерирую твою ебанутую судьбу...")

    try:
        image, caption, card_name = await asyncio.wait_for(generate_card(), timeout=10)

        # сохраняем в коллекцию
        user_id = callback.from_user.id
        if user_id not in user_cards:
            user_cards[user_id] = []

        user_cards[user_id].append(card_name)

        await callback.message.answer_photo(photo=image, caption=caption)

    except:
        await callback.message.answer("💀 Карта ушла в астрал... попробуй ещё раз")


# 📚 коллекция
@dp.callback_query(lambda c: c.data == "collection")
async def collection_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    cards = user_cards.get(user_id, [])

    if not cards:
        await callback.message.answer("📚 У тебя пока нихуя нет")
        return

    text = "📚 Твоя коллекция:\n\n"
    for c in cards:
        text += f"• {c}\n"

    await callback.message.answer(text)


# 🧪 fallback
@dp.message()
async def fallback(message: types.Message):
    await message.answer("Жми кнопки, не тупи 👇", reply_markup=get_keyboard())


# ▶️ запуск
async def main():
    print("Бот запущен 💀")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())