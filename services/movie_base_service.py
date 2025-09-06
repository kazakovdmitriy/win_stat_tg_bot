import os
from typing import List, Tuple
from pathlib import Path

from config import config


class MovieBaseService:
    def __init__(self):
        self.movie_folder = config.torrent_folders['🎬 Фильмы']
        self.extensions = config.movie_extensions

    def get_all_movies(self) -> List[Tuple[str, str]]:
        movies = []
        movie_path = Path(self.movie_folder)
        
        if not movie_path.exists():
            return movies
            
        for file_path in movie_path.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() in self.extensions:
                    # Используем stem для получения имени файла без расширения
                    movie_name = file_path.stem
                    # Преобразуем путь в строку для совместимости
                    full_path = str(file_path)
                    movies.append((movie_name, full_path))
        
        return movies
