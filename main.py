# main.py - Основной файл бота
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import DatabaseManager
from handlers import user, admin

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    # Проверяем конфигурацию
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен в переменных окружения!")
        return
    
    if not Config.ADMIN_IDS or Config.ADMIN_IDS == [0]:
        logger.warning("ADMIN_IDS не установлены! Функции администратора будут недоступны.")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключение роутеров
    dp.include_router(user.router)
    dp.include_router(admin.router)
    
    # Инициализация базы данных
    db = DatabaseManager()
    await db.init_db()
    logger.info("База данных инициализирована")
    
    # Информация о запуске
    logger.info("Бот запускается...")
    logger.info(f"Админы: {Config.ADMIN_IDS}")
    
    try:
        # Запуск бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот завершил работу")

if __name__ == "__main__":
    asyncio.run(main())