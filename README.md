# Win Stat Telegram Bot

Бот для вывода статистики Windows-машины (диски, CPU, память, сеть) по команде /stats.

## Установка

1. Скопируйте `.env.example` в `.env` и укажите свой токен Telegram-бота:
   ```
   cp .env.example .env
   ```
2. Инициализируйте окружение и установите зависимости через [uv](https://github.com/astral-sh/uv):
   ```
   uv venv .venv
   source .venv/bin/activate
   uv sync
   ```

## Запуск

Для запуска используйте:
```
uv run python bot.py
```

## Структура
- `services/` — сервисы для сбора информации
- `handlers/` — обработчики команд
- `config.py` — загрузка конфигурации и секретов

## Команды
- `/stats` — получить статистику системы 