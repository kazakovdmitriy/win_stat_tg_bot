import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    bot_token: str

    @staticmethod
    def from_env() -> 'Config':
        return Config(
            bot_token=os.getenv('BOT_TOKEN', '')
        )

config = Config.from_env() 