import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Tokenni environment variable orqali olish (masalan, Railway yoki boshqa serverlarda)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN o'rnatilmagan!")

# Adminlar ro'yxati: (id, username, telefon)
ADMINS = [
    {"id": 7752032178, "username": "adminusername1", "phone": "+998940898119"},
    # boshqalarni ham qo'shishingiz mumkin
]

# Foydalanuvchilar IDlarini saqlash uchun set
foydalanuvchilar = set()

# /start buyrug'i
async def start_handler(message: types.Message):
    foydalanuvchilar.add(message.from_user.id)
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "🛍 <b>Kerakli mahsulot yoki xizmat nomini yozing.</b>\n"
        "📨 Sizning so'rovingiz adminlarga yetkaziladi va ular tez orada siz bilan bog'lanishadi.\n\n"
        "✏️ <i>Masalan: logo, dizayn, web-sayt yaratish va boshqalar...</i>",
        parse_mode=ParseMode.HTML
    )

# Foydalanuvchidan kelgan matnni adminlarga yuborish va foydalanuvchiga adminlar bilan bog'lanish tugmalari
async def text_handler(message: types.Message, bot: Bot):
    foydalanuvchilar.add(message.from_user.id)

    user = message.from_user
    user_id = user.id
    user_identifier = f"@{user.username}" if user.username else f"id: <a href='tg://user?id={user_id}'>{user_id}</a>"
    text = message.text

    xabar = (
        f"💬 <b>Yangi so‘rov!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {user_identifier}\n"
        f"📩 <b>Xabar:</b> <i>{text}</i>"
    )

    keyboard = InlineKeyboardMarkup(row_width=1)
    for admin in ADMINS:
        if admin["username"]:
            keyboard.add(InlineKeyboardButton(
                text=f"📲 Telegram: @{admin['username']}",
                url=f"https://t.me/{admin['username']}"
            ))
        if admin["phone"]:
            keyboard.add(InlineKeyboardButton(
                text=f"📞 Qo'ng'iroq qilish: {admin['phone']}",
                url=f"tel:{admin['phone']}"
            ))

    for admin in ADMINS:
        try:
            await bot.send_message(admin["id"], xabar, parse_mode=ParseMode.HTML)
        except Exception as e:
            logging.error(f"Adminlarga xabar yuborishda xatolik: {e}")

    await message.answer(
        "✅ <b>So‘rovingiz qabul qilindi!</b>\n\n"
        "❗ Quyidagi adminlar bilan bog‘lanishingiz mumkin:\n\n"
        "👇 Tugmalardan birini bosing:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

# /reklama buyruq faqat adminlar uchun — barcha foydalanuvchilarga reklama yuboradi
async def reklama_handler(message: types.Message, bot: Bot):
    if message.from_user.id not in [admin["id"] for admin in ADMINS]:
        return await message.answer("🚫 Siz bu buyruqdan foydalana olmaysiz.")

    matn = message.text.replace("/reklama", "").strip()
    if not matn:
        return await message.answer(
            "❗ Iltimos, reklama matnini yozing.\nMasalan:\n/reklama 🎉 Yangi aksiyalar boshlandi!"
        )

    reklama_xabar = (
        "📢 <b>YANGI REKLAMA!</b>\n\n"
        f"{matn}\n\n"
        "🔔 Bizni kuzatib boring!"
    )

    count = 0
    for user_id in foydalanuvchilar:
        try:
            await bot.send_message(user_id, reklama_xabar, parse_mode=ParseMode.HTML)
            count += 1
        except Exception as e:
            logging.warning(f"Reklama yuborishda xatolik: {e}")

    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi!")

# /foydalanuvchilar buyruq faqat adminlar uchun — foydalanuvchilar sonini ko‘rsatadi
async def foydalanuvchilar_handler(message: types.Message):
    if message.from_user.id not in [admin["id"] for admin in ADMINS]:
        return await message.answer("🚫 Bu buyruq faqat administratorlar uchun.")

    await message.answer(
        f"👥 Botdan hozirgacha <b>{len(foydalanuvchilar)}</b> ta foydalanuvchi foydalangan.",
        parse_mode=ParseMode.HTML
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.message.register(reklama_handler, lambda message: message.text and message.text.startswith("/reklama"))
    dp.message.register(foydalanuvchilar_handler, Command("foydalanuvchilar"))
    dp.message.register(text_handler, lambda message: message.text and not message.text.startswith("/"))

    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
