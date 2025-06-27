import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    bot_token: str
    allowed_users: list[int]

    @staticmethod
    def from_env() -> 'Config':
        return Config(
            bot_token=os.getenv('BOT_TOKEN', ''),
            allowed_users=[int(uid) for uid in os.getenv('ALLOWED_USERS', '').split(',') if uid.strip().isdigit()]
        )

config = Config.from_env() 