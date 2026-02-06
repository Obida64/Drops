import json
import asyncio
from aiogram import F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from loader import bot, dp
from config import ADMIN_ID
from logger import logger

AVAILABLE_FILE = "../data/available.json"
ISSUED_FILE = "../data/issued.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@dp.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Купить Twitch Drop RUST", callback_data="buy")]
    ])

    await message.answer(
        "🔥 *RUST Twitch Drops*\n\n"
        "Автоматическая выдача аккаунтов.\n"
        "Без ожиданий и ручной работы.",
        reply_markup=kb,
        parse_mode="Markdown"
    )


@dp.callback_query(F.data == "buy")
async def buy(callback: CallbackQuery):
    available = load_json(AVAILABLE_FILE)
    keyboard = []

    for round_name, accounts in available.items():
        if accounts:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{round_name} · {len(accounts)} шт",
                    callback_data=f"round:{round_name}"
                )
            ])

    if not keyboard:
        await callback.answer("❌ Нет доступных дропов", show_alert=True)
        return

    await callback.message.edit_text(
        "🎯 *Выбери раунд Twitch Drops:*",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith("round:"))
async def issue_account(callback: CallbackQuery):
    round_name = callback.data.split(":", 1)[1]
    available = load_json(AVAILABLE_FILE)

    if round_name not in available or not available[round_name]:
        await callback.answer("❌ Аккаунты закончились", show_alert=True)
        return

    account = available[round_name].pop(0)
    save_json(AVAILABLE_FILE, available)

    issued = load_json(ISSUED_FILE)
    issued.append({
        "round": round_name,
        "account": account,
        "telegram_id": callback.from_user.id
    })
    save_json(ISSUED_FILE, issued)

    await callback.message.edit_text(
        f"✅ *Твой Twitch аккаунт*\n\n"
        f"`{account}`\n\n"
        "⚠️ *Сразу смени пароль!*",
        parse_mode="Markdown"
    )


@dp.message(F.text.startswith("/add"))
async def add_accounts(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    lines = message.text.splitlines()
    if len(lines) < 2:
        await message.answer("❌ Формат:\n/add Round 1\nlogin:pass")
        return

    round_name = lines[0].replace("/add", "").strip()
    available = load_json(AVAILABLE_FILE)

    available.setdefault(round_name, [])
    added = 0

    for acc in lines[1:]:
        if ":" in acc:
            available[round_name].append(acc.strip())
            added += 1

    save_json(AVAILABLE_FILE, available)
    await message.answer(f"✅ Добавлено: {added} аккаунтов в {round_name}")


async def main():
    logger.info("🚀 Бот запущен и слушает Telegram")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
