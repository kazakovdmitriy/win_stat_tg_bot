import os
from typing import List, Tuple

from config import config


class MovieBaseService:
    def __init__(self):
        self.movie_folder = config.torrent_folders['🎬 Фильмы']
        self.extensions = config.movie_extensions

    def get_all_movies(self) -> List[Tuple[str, str]]:
        movies = []
        for dirpath, _, filenames in os.walk(self.movie_folder):
            for filename in filenames:
                if os.path.splitext(filename)[1].lower() in self.extensions:
                    full_path = os.path.join(dirpath, filename)
                    movies.append((filename.split(".")[0], full_path))
        
        return movies
