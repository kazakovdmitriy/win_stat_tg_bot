import psutil
from typing import List, Dict
from services.logger import get_logger

logger = get_logger(__name__)


class SystemInfoService:
    @staticmethod
    def get_disks_info() -> List[Dict]:
        disks = []
        try:
            for part in psutil.disk_partitions():
                usage = psutil.disk_usage(part.mountpoint)
                disks.append({
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
        except Exception as e:
            logger.exception("Ошибка при получении информации о дисках")
        return disks

    @staticmethod
    def get_cpu_info() -> Dict:
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
        except Exception as e:
            logger.exception("Ошибка при получении информации о CPU")
            return {}

    @staticmethod
    def get_memory_info() -> Dict:
        try:
            mem = psutil.virtual_memory()
            return mem._asdict()
        except Exception as e:
            logger.exception("Ошибка при получении информации о памяти")
            return {}

    @staticmethod
    def get_network_info() -> Dict:
        try:
            net = psutil.net_io_counters(pernic=True)
            return {iface: data._asdict() for iface, data in net.items()}
        except Exception as e:
            logger.exception("Ошибка при получении информации о сети")
            return {} 