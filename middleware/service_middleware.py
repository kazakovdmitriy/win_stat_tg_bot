from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from services import TorrentService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, torrent_service: TorrentService):
        self.torrent_service = torrent_service
        
    async def __call__(self, handler, event, data):
        data['torrent_service'] = self.torrent_service
        return await handler(event, data)
