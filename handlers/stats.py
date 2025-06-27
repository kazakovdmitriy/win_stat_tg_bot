from aiogram import Router
from aiogram.types import Message
from services.system_info import SystemInfoService
from services.utils import format_system_stats

router = Router()

@router.message(commands=["stats"])
async def stats_handler(message: Message):
    disks = SystemInfoService.get_disks_info()
    cpu = SystemInfoService.get_cpu_info()
    mem = SystemInfoService.get_memory_info()
    net = SystemInfoService.get_network_info()

    text = format_system_stats(disks, cpu, mem, net)

    await message.answer(text, parse_mode="HTML") 