from aiogram import Router
from aiogram.types import Message
from services.system_info import SystemInfoService
from services.utils import format_system_stats
from services.keyboards import get_status_keyboard
from aiogram.filters import Command
from services.logger import get_logger
from config import config

router = Router()
logger = get_logger(__name__)


@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id not in config.allowed_users:
        return
    logger.info(f"Получен запрос /stats от пользователя {message.from_user.id}")
    try:
        disks = SystemInfoService.get_disks_info()
        cpu = SystemInfoService.get_cpu_info()
        mem = SystemInfoService.get_memory_info()
        net = SystemInfoService.get_network_info()
        text = format_system_stats(disks, cpu, mem, net)
        await message.answer(text, parse_mode="HTML", reply_markup=get_status_keyboard())
        logger.info(f"Успешно отправлена статистика пользователю {message.from_user.id}")
    except Exception as e:
        logger.exception("Ошибка при обработке команды /stats")
        await message.answer("Произошла ошибка при получении статистики.", reply_markup=get_status_keyboard()) 