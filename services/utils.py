def format_system_stats(disks, cpu, mem, net) -> str:
    def gb(val):
        return val / (1024 ** 3)

    text = "<b>📊 Статистика системы</b>\n"
    text += "\n<b>💾 Диски:</b>\n"
    for d in disks:
        text += (
            f"<b>{d['device']}</b> (<i>{d['mountpoint']}, {d['fstype']}</i>):\n"
            f" ├ Свободно: <b>{gb(d['free']):.1f} ГБ</b> из <b>{gb(d['total']):.1f} ГБ</b> (<i>{d['percent']}%</i>)\n"
        )
    text += f"\n<b>🖥 CPU:</b> <b>{cpu['cpu_percent']}%</b> загрузка, ядер: <b>{cpu['cpu_count']}</b>"
    if cpu['cpu_freq']:
        text += f"\n └ Частота: <b>{cpu['cpu_freq']['current']:.0f} МГц</b>"
    text += (
        f"\n\n<b>🧠 Память:</b> <b>{gb(mem['available']):.1f} ГБ</b> свободно из <b>{gb(mem['total']):.1f} ГБ</b>"
    )
    text += "\n\n<b>🌐 Сеть:</b>\n"
    for iface, data in net.items():
        text += (
            f"<b>{iface}</b>: отправлено <b>{gb(data['bytes_sent']):.1f} ГБ</b>, получено <b>{gb(data['bytes_recv']):.1f} ГБ</b>\n"
        )
    return text 