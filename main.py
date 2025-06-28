from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart
from aiogram.client.default import DefaultBotProperties
import asyncio
import os
from dotenv import load_dotenv

from handlers import register_handlers
from database import setup_db
from logger import setup_logger, log_error

load_dotenv()

# Настройка логирования
logger = setup_logger()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.error("BOT_TOKEN не найден в переменных окружения!")
    exit(1)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

register_handlers(dp)

async def on_startup():
    """Действия при запуске бота"""
    try:
        await setup_db()
        logger.info("База данных инициализирована")
        logger.info("Бот запущен успешно")
    except Exception as e:
        log_error(e, "startup")
        raise

async def on_shutdown():
    """Действия при остановке бота"""
    logger.info("Бот остановлен")

async def main():
    try:
        await on_startup()
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        log_error(e, "main")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
