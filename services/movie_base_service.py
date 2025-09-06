import os
from typing import List, Tuple
import sys

from config import config
from services.logger import get_logger

logger = get_logger(__name__)


class MovieBaseService:
    def __init__(self):
        self.movie_folder = config.torrent_folders['🎬 Фильмы']
        self.extensions = config.movie_extensions

    def get_all_movies(self) -> List[Tuple[str, str]]:
        logger.info(f"Movie folder: {self.movie_folder}")
        logger.info(f"Extensions: {self.extensions}")
        
        movies = []
        
        if not os.path.exists(self.movie_folder):
            logger.error(f"Directory does not exist: {self.movie_folder}")
            return movies
            
        try:
            for dirpath, dirnames, filenames in os.walk(self.movie_folder):
                for filename in filenames:
                    file_extension = os.path.splitext(filename)[1].lower()
                    logger.debug(f"Checking file: {filename}, extension: '{file_extension}'")
                    
                    if file_extension in self.extensions:
                        full_path = os.path.join(dirpath, filename)
                        
                        # Получаем размер файла
                        try:
                            file_size = os.path.getsize(full_path)
                            # Форматируем размер файла
                            size_formatted = self._format_file_size(file_size)
                            # Добавляем размер к имени файла
                            filename_with_size = f"[{size_formatted}] {os.path.splitext(filename)[0]}"
                        except OSError as e:
                            logger.warning(f"Could not get size for file {full_path}: {e}")
                            filename_with_size = os.path.splitext(filename)[0]
                        
                        movies.append((filename_with_size, full_path))
                        logger.debug(f"Added movie: {filename_with_size}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}", exc_info=True)
            return []
            
        logger.info(f"Total movies found: {len(movies)}")
        return movies

    def _format_file_size(self, size_bytes: int) -> str:
        """Форматирует размер файла в удобочитаемый формат"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
            
        if i == 0:  # байты
            return f"{int(size)}{size_names[i]}"
        elif size < 10:
            return f"{size:.1f}{size_names[i]}"
        else:
            return f"{int(size)}{size_names[i]}"
