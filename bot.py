import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# 📌 Главное меню
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="🧑‍⚕ Личный кабинет")
    kb.button(text="💊 Услуги")
    kb.button(text="📅 Записаться на приём")
    kb.button(text="🚑 Вызвать скорую")
    kb.button(text="📱 Мы в соц. сетях")
    kb.button(text="🎁 Акции")
    kb.adjust(2, 2, 2)
    return kb.as_markup(resize_keyboard=True)

# 📌 Подменю для записи
def appointment_menu():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📞 Позвонить")
    kb.button(text="💬 Написать в WhatsApp")
    kb.button(text="⬅ Назад")
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

# === Команды ===
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать в клинику <b>Мой Доктор</b>!", reply_markup=main_menu())

@dp.message(lambda m: m.text == "🧑‍⚕ Личный кабинет")
async def personal_cabinet(message: types.Message):
    await message.answer(
        "🔗 <b>Личный кабинет</b>",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Открыть",
                    web_app=WebAppInfo(url="https://mydoctorarmavir.ru/personal/profile/")
                )],
                [types.InlineKeyboardButton(
                    text="⬅ Вернуться в меню",
                    callback_data="back_main"
                )]
            ]
        )
    )

@dp.message(lambda m: m.text == "💊 Услуги")
async def services(message: types.Message):
    await message.answer(
        "Наши услуги:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Открыть",
                    web_app=WebAppInfo(url="https://mydoctorarmavir.ru/services/")
                )],
                [types.InlineKeyboardButton(
                    text="⬅ Вернуться в меню",
                    callback_data="back_main"
                )]
            ]
        )
    )

@dp.message(lambda m: m.text == "📅 Записаться на приём")
async def appointment(message: types.Message):
    await message.answer("Выберите способ записи:", reply_markup=appointment_menu())

@dp.message(lambda m: m.text == "📞 Позвонить")
async def call_clinic(message: types.Message):
    await message.answer("📞 Нажмите на номер для звонка: +79898003007")
    await message.answer(
        '<a href="tel:+79898003007">Позвонить</a>',
        disable_web_page_preview=True
    )

@dp.message(lambda m: m.text == "💬 Написать в WhatsApp")
async def whatsapp(message: types.Message):
    await message.answer(
        '<a href="https://api.whatsapp.com/send/?phone=79898003007&text=Здравствуйте%21&type=phone_number&app_absent=0">Написать в WhatsApp</a>',
        disable_web_page_preview=True
    )

@dp.message(lambda m: m.text == "🚑 Вызвать скорую")
async def call_ambulance(message: types.Message):
    await message.answer("🚑 Нажмите для вызова скорой: +78002501850")
    await message.answer(
        '<a href="tel:+78002501850">Вызвать скорую</a>',
        disable_web_page_preview=True
    )

@dp.message(lambda m: m.text == "📱 Мы в соц. сетях")
async def social_links(message: types.Message):
    await message.answer(
        "Наши соц. сети:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Открыть",
                    web_app=WebAppInfo(url="https://taplink.cc/mydoctor_armavir")
                )],
                [types.InlineKeyboardButton(
                    text="⬅ Вернуться в меню",
                    callback_data="back_main"
                )]
            ]
        )
    )

@dp.message(lambda m: m.text == "🎁 Акции")
async def promotions(message: types.Message):
    await message.answer(
        "Текущие акции:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Открыть",
                    web_app=WebAppInfo(url="https://mydoctorarmavir.ru/clinic/promotions/")
                )],
                [types.InlineKeyboardButton(
                    text="⬅ Вернуться в меню",
                    callback_data="back_main"
                )]
            ]
        )
    )

@dp.message(lambda m: m.text == "⬅ Назад")
async def go_back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu())

# 📌 Обработчик возврата в меню
@dp.callback_query(lambda c: c.data == "back_main")
async def back_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("Главное меню:", reply_markup=main_menu())
    await callback.answer()

# === Запуск бота ===
if __name__ == "__main__":
    import asyncio
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main())
