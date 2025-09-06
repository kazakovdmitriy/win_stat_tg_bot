import os
from typing import List, Tuple
from pathlib import Path
import sys

from config import config
from services.logger import get_logger


logger = get_logger(__name__)


class MovieBaseService:
    def __init__(self):
        self.movie_folder = config.torrent_folders['🎬 Фильмы']
        self.extensions = config.movie_extensions

    def get_all_movies(self) -> List[Tuple[str, str]]:
        logger.info(f"Python version: {sys.version}")
        logger.info(f"OS: {os.name}")
        logger.info(f"Movie folder: {self.movie_folder}")
        logger.info(f"Extensions: {self.extensions}")
        
        movies = []
        
        if not os.path.exists(self.movie_folder):
            logger.error(f"Directory does not exist: {self.movie_folder}")
            return movies
            
        logger.info(f"Directory exists: {os.path.exists(self.movie_folder)}")
        
        try:
            for dirpath, dirnames, filenames in os.walk(self.movie_folder):
                logger.debug(f"Scanning directory: {dirpath}")
                logger.debug(f"Files found: {len(filenames)}")
                for filename in filenames:
                    file_extension = os.path.splitext(filename)[1].lower()
                    logger.debug(f"Checking file: {filename}, extension: {file_extension}")
                    if file_extension in self.extensions:
                        full_path = os.path.join(dirpath, filename)
                        filename_without_ext = os.path.splitext(filename)[0]
                        logger.debug(f"Adding movie: {filename_without_ext}")
                        movies.append((filename_without_ext, full_path))
        except Exception as e:
            logger.error(f"Error scanning directory: {e}", exc_info=True)
            return []
            
        logger.info(f"Total movies found: {len(movies)}")
        return movies
