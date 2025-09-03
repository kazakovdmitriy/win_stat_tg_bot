from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import aiohttp
import os
import re
from urllib.parse import urlparse, unquote

from services.torrent_service import TorrentService
from services.keyboards import get_torrent_folders_keyboard, get_main_keyboard
from services.logger import get_logger
from config import config

router = Router()
logger = get_logger(__name__)

# Словарь для хранения временных данных о торрент файлах пользователей
user_torrent_data = {}

class TorrentState(StatesGroup):
    viewing = State()
    

def parse_content_disposition(content_disposition):
    """Парсит заголовок Content-Disposition и извлекает имя файла"""
    if not content_disposition:
        return None
    
    # Пытаемся извлечь имя файла из заголовка
    filename_match = re.search(r'filename\*?=["\']?(?:UTF-\d["\']*)?([^;"\']+)["\']?', content_disposition)
    if filename_match:
        filename = filename_match.group(1)
        # Декодируем URL-encoded строку
        filename = unquote(filename)
        return filename
    
    # Альтернативный вариант поиска имени файла
    filename_match = re.search(r'filename=["\']([^"\']+)["\']', content_disposition)
    if filename_match:
        return filename_match.group(1)


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


@router.message(Command("найти"))
async def torrent_search_handler(message: Message, command: CommandObject, state: FSMContext, torrent_service: TorrentService):
    if message.from_user.id not in config.allowed_users:
        return
    
    args = command.args
    
    if args:
        blocks = torrent_service.search_torrent(args)
        
        await state.set_state(TorrentState.viewing)
        # await state.update_data(torrent_blocks=blocks)
        
        message_ids = []
        
        for i, block in enumerate(blocks):
            
            text = torrent_service.format_message(block)
            button = InlineKeyboardButton(text="📥 Скачать", callback_data=f"download_{i}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

            send_message = await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
            
            message_ids.append(send_message.message_id)
            
            await state.update_data(
                torrent_blocks=blocks,
                search_message_ids=message_ids,
                command_message_id=message.message_id
            )
            
        # Добавляем сообщение с кнопкой очистки поиска
        clear_button = InlineKeyboardButton(text="🗑️ Очистить", callback_data="clear_search")
        clear_keyboard = InlineKeyboardMarkup(inline_keyboard=[[clear_button]])
        clear_message = await message.answer(
            "Вы можете очистить все результаты поиска, если не нашли нужный торрент:",
            reply_markup=clear_keyboard
        )
        message_ids.append(clear_message.message_id)
    else:
        text = "Для поиска введите название фильма после команды. Например: /search Матрица 4"
        await message.answer(text, parse_mode="HTML", reply_markup=get_main_keyboard())


@router.callback_query(lambda callback: callback.data == 'clear_search')
async def clear_search_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик очистки результатов поиска"""
    if callback.from_user.id not in config.allowed_users:
        await callback.answer("❌ Доступ запрещен")
        return
    
    user_data = await state.get_data()
    search_message_ids = user_data.get('search_message_ids', [])
    command_message_id = user_data.get('command_message_id')
    
    # Удаляем все сообщения с результатами поиска
    deleted_count = 0
    for msg_id in search_message_ids:
        try:
            await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения {msg_id}: {e}")
    
    # Также удаляем оригинальное сообщение с командой /search
    try:
        await bot.delete_message(chat_id=callback.from_user.id, message_id=command_message_id)
        deleted_count += 1
    except Exception as e:
        logger.error(f"Ошибка при удалении команды {command_message_id}: {e}")
    
    # Отправляем подтверждение об очистке
    await callback.answer(f"🗑️ Удалено {deleted_count} сообщений", show_alert=False)
    
    # Очищаем состояние
    await state.clear()
    
    # Отправляем сообщение о том, что поиск очищен
    await callback.message.answer(
        "✅ Результаты поиска очищены. Вы можете начать новый поиск с помощью команды /search",
        reply_markup=get_main_keyboard()
    )

        
@router.callback_query(lambda callback: callback.data.startswith('download_'))
async def torrent_download(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик скачивания торрента по ссылке"""
    if callback.from_user.id not in config.allowed_users:
        await callback.answer("❌ Доступ запрещен")
        return
    
    user_data = await state.get_data()
    blocks = user_data.get('torrent_blocks', [])
    search_message_ids = user_data.get('search_message_ids', [])
    command_message_id = user_data.get('command_message_id')
    index = int(callback.data.split("_")[1])

    if index < len(blocks):
        selected_block = blocks[index]
        await callback.answer("📥 Загружаем торрент...", show_alert=False)

        try:
            # Удаляем все сообщения с результатами поиска
            for msg_id in search_message_ids:
                try:
                    await bot.delete_message(chat_id=callback.from_user.id, message_id=msg_id)
                except Exception as e:
                    logger.error(f"Ошибка при удалении сообщения {msg_id}: {e}")
            
            # Также удаляем оригинальное сообщение с командой /search
            try:
                await bot.delete_message(chat_id=callback.from_user.id, message_id=command_message_id)
            except Exception as e:
                logger.error(f"Ошибка при удалении команды {command_message_id}: {e}")
            
            # Скачиваем .torrent файл по ссылке
            async with aiohttp.ClientSession() as session:
                async with session.get(selected_block["Link"]) as response:
                    if response.status == 200:
                        # Получаем имя файла из заголовка Content-Disposition
                        content_disposition = response.headers.get('Content-Disposition')
                        filename = parse_content_disposition(content_disposition)
                        
                        # Если не удалось извлечь имя из заголовка, используем заголовок из URL
                        if not filename:
                            parsed_url = urlparse(selected_block["Link"])
                            filename = os.path.basename(parsed_url.path)
                            
                            # Убеждаемся, что у файла есть расширение .torrent
                            if not filename.endswith('.torrent'):
                                # Используем заголовок блока для создания имени файла
                                safe_title = "".join(c for c in selected_block["Title"] if c.isalnum() or c in (' ', '.', '_')).rstrip()
                                filename = f"{safe_title}.torrent"
                        
                        # Читаем содержимое файла
                        file_data = await response.read()
                        
                        # Сохраняем информацию о файле для последующего использования
                        user_torrent_data[callback.from_user.id] = {
                            'file_data': file_data,
                            'file_name': filename
                        }
                        
                        # Предлагаем выбрать папку для сохранения
                        await callback.message.answer(
                            f"📥 <b>Получен торрент файл:</b> <code>{filename}</code>\n\n"
                            "📁 Куда вы хотите сохранить этот файл?",
                            parse_mode="HTML",
                            reply_markup=get_torrent_folders_keyboard()
                        )
                    else:
                        await callback.answer("❌ Не удалось скачать файл", show_alert=True)
        except Exception as e:
            logger.exception("Ошибка при скачивании торрент файла по ссылке")
            await callback.answer("❌ Ошибка при загрузке файла", show_alert=True)
    else:
        await callback.answer("❌ Ошибка: блок не найден", show_alert=True)


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
            await callback.answer("❌ Данные о файле не найдены. Попробуйте еще раз.")
            return
        
        # Получаем данные о файле
        file_data = user_torrent_data[user_id].get('file_data')
        file_name = user_torrent_data[user_id].get('file_name')
        
        if not file_data or not file_name:
            await callback.answer("❌ Ошибка: данные файла повреждены")
            return
        
        await callback.answer("💾 Сохраняю файл...")
        
        # Сохраняем файл
        saved_path = await TorrentService.save_torrent_file_from_bytes(
            file_data, file_name, folder_name
        )
        
        if saved_path:
            success_text = (
                f"✅ <b>Файл успешно сохранен!</b>\n\n"
                f"📁 <b>Папка:</b> {folder_name}\n"
                f"📄 <b>Файл:</b> <code>{file_name}</code>\n"
                f"💾 <b>Путь:</b> <code>{saved_path}</code>"
            )
            
            await callback.message.edit_text(
                success_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Торрент файл {file_name} успешно сохранен пользователем {user_id} в папку {folder_name}")
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