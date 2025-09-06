import os
from typing import List, Dict
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    bot_token: str
    jackett_token: str
    jackett_url: str
    allowed_users: List[int]
    torrent_limit: int
    torrent_folders: Dict[str, str]
    movie_extensions: List[str]
    movie_root_folder: str

    @staticmethod
    def from_env() -> 'Config':
        # Пути к папкам для торрентов (можете изменить на свои пути)
        torrent_folders = {
            "🎬 Фильмы": r"D:\New\Movie",
            "📺 Сериалы": r"D:\New\Series", 
            "🎮 Игры": r"D:\New\Game"
        }

        movie_root_folder = "D:\Media\Movie"

        movie_extensions = {
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
            '.webm', '.m4v', '.3gp', '.ts', '.mpeg', '.mpg'
        }
        
        return Config(
            bot_token=os.getenv('BOT_TOKEN', ''),
            jackett_token=os.getenv('JACKETT_TOKEN', ''),
            jackett_url=os.getenv('JACKETT_URL', '127.0.0.1:9117'),
            torrent_limit=int(os.getenv('TORRENT_LIMIT', '10')),
            allowed_users=[int(uid) for uid in os.getenv('ALLOWED_USERS', '').split(',') if uid.strip().isdigit()],
            torrent_folders=torrent_folders,
            movie_extensions=movie_extensions,
            movie_root_folder=movie_root_folder
        )


config = Config.from_env()
