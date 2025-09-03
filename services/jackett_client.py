import requests
from services.logger import get_logger
from typing import List, Dict
from urllib.parse import quote_plus


class JackettClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """
        Инициализация клиента Jackett
        
        :param base_url: Базовый URL Jackett (например, "http://192.168.1.103:9117")
        :param api_key: API ключ Jackett
        :param timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        self.logger = get_logger(__name__)

    def search(self, query: str, indexer: str = "all", category: str = None, 
               limit: int = 20) -> List[Dict]:
        """
        Поиск торрентов
        
        :param query: Поисковый запрос
        :param indexer: Индексер (по умолчанию "all" - все индексаторы)
        :param category: Категория для фильтрации
        :param limit: Максимальное количество результатов
        :return: Список результатов поиска
        """
        try:
            # Формируем URL запроса
            url = f"http://{self.base_url}/api/v2.0/indexers/{indexer}/results"
            params = {
                "apikey": self.api_key,
                "Query": query
            }
            
            if category:
                params["Category"] = category
            
            # Выполняем запрос
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Парсим ответ
            data = response.json()
            results = data.get("Results", [])
            
            # Сортируем по количеству сидов (если есть) и ограничиваем количество
            if results and "Size" in results[0]:
                results.sort(key=lambda x: x.get("Size", 0), reverse=True)
            
            return results[:limit]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при выполнении запроса: {e}")
            return []
        except ValueError as e:
            self.logger.error(f"Ошибка при парсинге JSON: {e}")
            return []

    def get_indexers(self) -> List[Dict]:
        """
        Получение списка всех индексеров
        
        :return: Список индексеров
        """
        try:
            url = f"{self.base_url}/api/v2.0/indexers"
            response = self.session.get(url, params={"apikey": self.api_key}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении список индексеров: {e}")
            return []

    def format_result(self, result: Dict) -> str:
        """
        Форматирование результата для отправки в Telegram
        
        :param result: Результат поиска
        :return: Отформатированная строка
        """
        title = result.get("Title", "Без названия")
        tracker = result.get("Tracker", "Неизвестный трекер")
        size = self._format_size(result.get("Size", 0))
        seeders = result.get("Seeders", "N/A")
        leechers = result.get("Peers", "N/A")
        if leechers != "N/A" and seeders != "N/A":
            leechers = leechers - seeders  # Peers = Seeders + Leechers
        
        # Формируем сообщение
        message = (
            f"🎬 <b>{title}</b>\n"
            f"📊 Трекер: <code>{tracker}</code>\n"
            f"📦 Размер: <code>{size}</code>\n"
            f"👤 Сиды: <code>{seeders}</code>\n"
            f"⬇️ Личи: <code>{leechers}</code>\n"
        )
        
        # Добавляем ссылку на магнит или детали
        # if "MagnetUri" in result and result["MagnetUri"]:
        #     message += f"🧲 <a href='{result['MagnetUri']}'>Магнет-ссылка</a>\n"
        # if "Link" in result and result["Link"]:
        #     message += f"<a href='{result['Link']}'>.torrent</a>\n"
        # elif "Details" in result and result["Details"]:
        #     message += f"🔗 <a href='{result['Details']}'>Ссылка на детали</a>\n"
        
        return message

    def _format_size(self, size_bytes: int) -> str:
        """
        Форматирование размера файла в читаемый вид
        
        :param size_bytes: Размер в байтах
        :return: Отформатированная строка размера
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.2f} {size_names[i]}"
