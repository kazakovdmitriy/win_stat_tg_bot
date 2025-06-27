def format_system_stats(disks, cpu, mem, net) -> str:
    text = "<b>Статистика системы:</b>\n"
    text += "\n<b>Диски:</b>\n"
    for d in disks:
        text += (f"{d['device']} ({d['mountpoint']}, {d['fstype']}): "
                 f"Свободно {d['free'] // (1024**3)}ГБ из {d['total'] // (1024**3)}ГБ ({d['percent']}%)\n")
    text += f"\n<b>CPU:</b> {cpu['cpu_percent']}% загрузка, ядер: {cpu['cpu_count']}\n"
    if cpu['cpu_freq']:
        text += f"Частота: {cpu['cpu_freq']['current']:.0f} MHz\n"
    text += f"\n<b>Память:</b> {mem['available'] // (1024**2)}МБ свободно из {mem['total'] // (1024**2)}МБ\n"
    text += "\n<b>Сеть:</b>\n"
    for iface, data in net.items():
        text += (f"{iface}: отправлено {data['bytes_sent'] // (1024**2)}МБ, получено {data['bytes_recv'] // (1024**2)}МБ\n")
    return text 