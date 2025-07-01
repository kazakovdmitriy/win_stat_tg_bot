import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    bot_token: str
    allowed_users: list[int]
    torrent_folders: dict[str, str]

    @staticmethod
    def from_env() -> 'Config':
        # Пути к папкам для торрентов (можете изменить на свои пути)
        torrent_folders = {
            "🎬 Фильмы": r"D:\New\Movie",
            "📺 Сериалы": r"D:\New\Series", 
            "🎮 Игры": r"D:\New\Game"
        }
        
        return Config(
            bot_token=os.getenv('BOT_TOKEN', ''),
            allowed_users=[int(uid) for uid in os.getenv('ALLOWED_USERS', '').split(',') if uid.strip().isdigit()],
            torrent_folders=torrent_folders
        )

config = Config.from_env() 