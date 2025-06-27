import psutil
from typing import List, Dict


class SystemInfoService:
    @staticmethod
    def get_disks_info() -> List[Dict]:
        disks = []
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
        return disks

    @staticmethod
    def get_cpu_info() -> Dict:
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }

    @staticmethod
    def get_memory_info() -> Dict:
        mem = psutil.virtual_memory()
        return mem._asdict()

    @staticmethod
    def get_network_info() -> Dict:
        net = psutil.net_io_counters(pernic=True)
        return {iface: data._asdict() for iface, data in net.items()} 