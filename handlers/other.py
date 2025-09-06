from aiogram import Router
from aiogram.types import Message
from services.keyboards import get_main_keyboard
from config import config

from services.logger import get_logger

logger = get_logger(__name__)

router = Router()

@router.message()
async def all_other_handler(message: Message):
    """
    Обрабатывает все прочие сообщения и отправляет клавиатуру с кнопкой статуса, только если пользователь разрешён.
    """
    
    logger.info(f"Пользователь: {message.from_user.id}, пишет: {message.text}")
    
    if message.from_user.id not in config.allowed_users:
        return
    await message.answer(
        "🤖 Привет! Используйте команды или кнопки:\n\n"
        "📊 Для получения статуса системы\n"
        "🧲 Отправьте .torrent файл для сохранения\n"
        "💬 Команда /torrent для справки",
        reply_markup=get_main_keyboard()
    )
