import os
from pathlib import Path
from typing import Optional, List
from aiogram.types import Document
from config import config
from services.logger import get_logger
from services import JackettClient

logger = get_logger(__name__)


class TorrentService:
    """Сервис для работы с торрент файлами"""
    def __init__(self):
        self.jackett = JackettClient(base_url=config.jackett_url, 
                                     api_key=config.jackett_token)
    
    @staticmethod
    def get_available_folders() -> dict[str, str]:
        """Получить доступные папки для сохранения торрентов"""
        return config.torrent_folders
    
    @staticmethod
    async def save_torrent_file(document: Document, bot, folder_name: str) -> Optional[str]:
        """
        Сохранить торрент файл в указанную папку
        
        Args:
            document: Документ с торрент файлом
            bot: Экземпляр бота для скачивания файла
            folder_name: Название папки (ключ из torrent_folders)
            
        Returns:
            Путь к сохраненному файлу или None в случае ошибки
        """
        try:
            if folder_name not in config.torrent_folders:
                logger.error(f"Неизвестная папка: {folder_name}")
                return None
                
            folder_path = Path(config.torrent_folders[folder_name])
            
            # Создаем папку если её нет
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Проверяем что файл действительно .torrent
            if not document.file_name.lower().endswith('.torrent'):
                logger.error(f"Файл {document.file_name} не является .torrent файлом")
                return None
            
            # Формируем путь для сохранения
            file_path = folder_path / document.file_name
            
            # Если файл уже существует, добавляем суффикс
            counter = 1
            original_path = file_path
            while file_path.exists():
                name_without_ext = original_path.stem
                file_path = folder_path / f"{name_without_ext}_{counter}.torrent"
                counter += 1
            
            # Скачиваем файл
            file_info = await bot.get_file(document.file_id)
            await bot.download_file(file_info.file_path, file_path)
            
            logger.info(f"Торрент файл {document.file_name} сохранен в {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.exception(f"Ошибка при сохранении торрент файла: {e}")
            return None
    
    @staticmethod
    def validate_torrent_folders() -> bool:
        """Проверить доступность папок для торрентов"""
        try:
            for folder_name, folder_path in config.torrent_folders.items():
                path = Path(folder_path)
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Папка {folder_name} доступна: {folder_path}")
                except Exception as e:
                    logger.error(f"Не удается создать папку {folder_name}: {folder_path}, ошибка: {e}")
                    return False
            return True
        except Exception as e:
            logger.exception(f"Ошибка при проверке папок торрентов: {e}")
            return False
        
    @staticmethod
    async def save_torrent_file_from_bytes(file_data: bytes, file_name: str, folder_name: str) -> str:
        """Сохраняет торрент-файл из байтов в указанную папку"""
        if folder_name not in config.torrent_folders:
            logger.error(f"Папка {folder_name} не найдена в конфигурации")
            return None

        folder_path = config.torrent_folders[folder_name]

        # Проверяем существование папки
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Полный путь к файлу
        full_path = os.path.join(folder_path, file_name)

        try:
            # Сохраняем файл
            with open(full_path, 'wb') as f:
                f.write(file_data)

            logger.info(f"Торрент файл сохранен: {full_path}")
            return full_path

        except Exception as e:
            logger.exception(f"Ошибка при сохранении торрент файла {file_name} в папку {folder_path}")
            return None

    def search_torrent(self, query: str, limit: int = 10) -> Optional[List[dict]]:
        return self.jackett.search(query=query, indexer="rutracker", limit=limit)
    
    def format_message(self, message: dict) -> str:
        return self.jackett.format_result(message)
