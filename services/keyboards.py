from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import config


def get_torrent_folders_keyboard():
    """Создать инлайн клавиатуру для выбора папки торрента"""
    buttons = []
    
    # Создаем кнопки для каждой папки из конфигурации
    for folder_display_name in config.torrent_folders.keys():
        button = InlineKeyboardButton(
            text=folder_display_name,
            callback_data=f"torrent_folder:{folder_display_name}"
        )
        buttons.append([button])
    
    # Добавляем кнопку отмены
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="torrent_cancel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_keyboard():
    """Основная клавиатура с добавлением кнопки для работы с торрентами"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Получить статус")],
        ],
        resize_keyboard=True
    ) 