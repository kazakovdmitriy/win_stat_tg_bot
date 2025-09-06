from aiogram import BaseMiddleware
from services import TorrentService, MovieBaseService


class ServiceMiddleware(BaseMiddleware):
    def __init__(self, 
                 torrent_service: TorrentService, 
                 movie_service: MovieBaseService):
        self.torrent_service = torrent_service
        self.movie_service = movie_service
        
    async def __call__(self, handler, event, data):
        data['torrent_service'] = self.torrent_service
        data['movie_service'] = self.movie_service
        return await handler(event, data)
