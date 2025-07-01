from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, Document
from aiogram.filters import Command
from services.torrent_service import TorrentService
from services.keyboards import get_torrent_folders_keyboard, get_main_keyboard
from services.logger import get_logger
from config import config

router = Router()
logger = get_logger(__name__)

# Словарь для хранения временных данных о торрент файлах пользователей
user_torrent_data = {}


@router.message(Command("torrent"))
async def torrent_help_handler(message: Message):
    """Обработчик команды /torrent - показывает справку"""
    if message.from_user.id not in config.allowed_users:
        return
    
    help_text = (
        "🧲 <b>Работа с торрент файлами</b>\n\n"
        "Просто отправьте мне .torrent файл, и я предложу выбрать папку для сохранения.\n\n"
        "📁 <b>Доступные папки:</b>\n"
    )
    
    for folder_name, folder_path in config.torrent_folders.items():
        help_text += f"• {folder_name}: <code>{folder_path}</code>\n"
    
    await message.answer(help_text, parse_mode="HTML", reply_markup=get_main_keyboard())


@router.message(lambda message: message.document and message.document.file_name and 
                message.document.file_name.lower().endswith('.torrent'))
async def torrent_file_handler(message: Message, bot: Bot):
    """Обработчик получения .torrent файла"""
    if message.from_user.id not in config.allowed_users:
        return
    
    logger.info(f"Получен торрент файл {message.document.file_name} от пользователя {message.from_user.id}")
    
    try:
        # Сохраняем информацию о файле для последующего использования
        user_torrent_data[message.from_user.id] = {
            'document': message.document,
            'message_id': message.message_id
        }
        
        await message.answer(
            f"📥 <b>Получен торрент файл:</b> <code>{message.document.file_name}</code>\n\n"
            "📁 Куда вы хотите сохранить этот файл?",
            parse_mode="HTML",
            reply_markup=get_torrent_folders_keyboard()
        )
        
    except Exception as e:
        logger.exception("Ошибка при обработке торрент файла")
        await message.answer(
            "❌ Произошла ошибка при обработке файла. Попробуйте еще раз.",
            reply_markup=get_main_keyboard()
        )


@router.callback_query(lambda callback: callback.data.startswith('torrent_folder:'))
async def torrent_folder_callback_handler(callback: CallbackQuery, bot: Bot):
    """Обработчик выбора папки для сохранения торрента"""
    if callback.from_user.id not in config.allowed_users:
        await callback.answer("❌ Доступ запрещен")
        return
    
    try:
        folder_name = callback.data.split(':', 1)[1]
        user_id = callback.from_user.id
        
        # Проверяем, есть ли данные о файле пользователя
        if user_id not in user_torrent_data:
            await callback.answer("❌ Данные о файле не найдены. Отправьте файл заново.")
            return
        
        document = user_torrent_data[user_id]['document']
        
        await callback.answer("💾 Сохраняю файл...")
        
        # Сохраняем файл
        saved_path = await TorrentService.save_torrent_file(document, bot, folder_name)
        
        if saved_path:
            success_text = (
                f"✅ <b>Файл успешно сохранен!</b>\n\n"
                f"📁 <b>Папка:</b> {folder_name}\n"
                f"📄 <b>Файл:</b> <code>{document.file_name}</code>\n"
                f"💾 <b>Путь:</b> <code>{saved_path}</code>"
            )
            
            await callback.message.edit_text(
                success_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Торрент файл {document.file_name} успешно сохранен пользователем {user_id} в папку {folder_name}")
        else:
            await callback.message.edit_text(
                "❌ <b>Ошибка при сохранении файла!</b>\n\n"
                "Проверьте доступность папки и попробуйте еще раз.",
                parse_mode="HTML"
            )
        
        # Очищаем временные данные
        if user_id in user_torrent_data:
            del user_torrent_data[user_id]
            
    except Exception as e:
        logger.exception("Ошибка при сохранении торрент файла")
        await callback.answer("❌ Произошла ошибка при сохранении")
        await callback.message.edit_text(
            "❌ <b>Произошла ошибка при сохранении файла!</b>\n\n"
            "Попробуйте еще раз.",
            parse_mode="HTML"
        )


@router.callback_query(lambda callback: callback.data == 'torrent_cancel')
async def torrent_cancel_callback_handler(callback: CallbackQuery):
    """Обработчик отмены сохранения торрента"""
    if callback.from_user.id not in config.allowed_users:
        await callback.answer("❌ Доступ запрещен")
        return
    
    user_id = callback.from_user.id
    
    # Очищаем временные данные
    if user_id in user_torrent_data:
        del user_torrent_data[user_id]
    
    await callback.answer("❌ Отменено")
    await callback.message.edit_text(
        "❌ <b>Сохранение торрент файла отменено</b>",
        parse_mode="HTML"
    )
    
    logger.info(f"Пользователь {user_id} отменил сохранение торрент файла") 