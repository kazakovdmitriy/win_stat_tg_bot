from aiogram import Router
from aiogram.types import Message
from services.keyboards import get_status_keyboard
from config import config

router = Router()

@router.message()
async def all_other_handler(message: Message):
    """
    Обрабатывает все прочие сообщения и отправляет клавиатуру с кнопкой статуса, только если пользователь разрешён.
    """
    if message.from_user.id not in config.allowed_users:
        return
    await message.answer(
        "Пожалуйста, используйте кнопку для получения статуса системы:",
        reply_markup=get_status_keyboard()
    ) 