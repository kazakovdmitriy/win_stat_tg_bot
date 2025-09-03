import sys
import requests

from config import config


def send_message(text, user_id):
    url = f'https://api.telegram.org/bot{config.bot_token}/sendMessage'
    data = {
        'chat_id': user_id,
        'text': text
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Ошибка отправки сообщения:", e)


if __name__ == '__main__':
    torrent_name = sys.argv[1] if len(sys.argv) > 1 else 'Неизвестный торрент'
    label = sys.argv[2] if len(sys.argv) > 2 else 'Без метки'
    file_path = sys.argv[3] if len(sys.argv) > 3 else 'Путь не указан'

    message = f"✅ Загрузка завершена!\n\n торрент: {torrent_name}\n метка: {label}\n путь: {file_path}"
    
    for user_id in config.allowed_users:
        send_message(message, user_id)
