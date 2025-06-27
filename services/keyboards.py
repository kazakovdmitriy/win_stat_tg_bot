from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_status_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Получить статус")],
        ],
        resize_keyboard=True
    ) 