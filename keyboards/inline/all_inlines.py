from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from keyboards.tests import test_uz

langs = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="ru")
        ]
    ]
)

start_test_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Unda testimizga marhamat 🚀", callback_data="start_test_uz")
        ]
    ]
)

start_test_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Жмите сюда для старта 🚀", callback_data="start_test_ru")
        ]
    ]
)

application = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Sinov darsiga yozilish🤩", callback_data='application')
        ]
    ]
)

application_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Записаться на пробное занятие🤩", callback_data='application_ru')
        ]
    ]
)

filials = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Yunusobod📍", callback_data='yunusobod')
        ],
        [
            InlineKeyboardButton("Tinchlik📍", callback_data='tinchlik')
        ],
        [
            InlineKeyboardButton("Chilonzor - Qutbiniso📍", callback_data='chilonzor')
        ],
        [
            InlineKeyboardButton("Sergeli📍", callback_data='sergeli')
        ]
    ]
)

filials_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("Юнусабад📍", callback_data='yunusobod')
        ],
        [
            InlineKeyboardButton("Тинчлик📍", callback_data='tinchlik')
        ],
        [
            InlineKeyboardButton("Чиланзар-Кутибнисо📍", callback_data='chilonzor')
        ],
        [
            InlineKeyboardButton("Сергели📍", callback_data='sergeli')
        ]
    ]
)

contact = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Bog'lanish", callback_data='contact')
        ]
    ]
)

contact_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Связь с Администратором", callback_data='contact_ru')
        ]
    ]
)


area_uz = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Toshkent shahri", callback_data='shahar')
        ],
        [
            InlineKeyboardButton(text="Toshkent viloyati", callback_data='viloyat')
        ],
        [
            InlineKeyboardButton(text="Boshqa hudud", callback_data='boshqa')
        ]
    ]
)

area_ru = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Город Ташкент", callback_data='shahar')
        ],
        [
            InlineKeyboardButton(text="Ташкентская область", callback_data='viloyat')
        ],
        [
            InlineKeyboardButton(text="Другой регион", callback_data='boshqa')
        ]
    ]
)