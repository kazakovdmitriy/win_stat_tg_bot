import asyncio
from aiogram import Bot, Dispatcher
from config import config
from handlers import all_routers

async def main():
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    for router in all_routers:
        dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 