from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

phone_uz = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Mening raqamim", request_contact=True)
        ]
    ], resize_keyboard=True
)

phone_ru = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📞 Мой номер", request_contact=True)
        ]
    ], resize_keyboard=True
)