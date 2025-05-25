# config.py - Конфигурация и настройки
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Класс конфигурации бота"""
    
    # Токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # ID администраторов
    ADMIN_IDS = []
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    if admin_ids_str:
        try:
            ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
        except ValueError:
            print("Ошибка: Некорректные ADMIN_IDS в .env файле")
    
    # URL базы данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///bot_database.db')
    
    @classmethod
    def validate(cls):
        """Валидация конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в переменных окружения!")
        
        if not cls.ADMIN_IDS:
            print("Предупреждение: ADMIN_IDS не установлены. Админ функции будут недоступны.")
        
        return True