import logging
import logging.handlers
import os
from datetime import datetime

def setup_logger():
    """Настройка логирования только в консоль и только уровня ERROR"""
    
    # Настраиваем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Хендлер только для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настраиваем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    
    # Очищаем существующие хендлеры и добавляем только консольный
    logger.handlers.clear()
    logger.addHandler(console_handler)
    
    return logger

def log_error(error: Exception, context: str = ""):
    """Логирование ошибок"""
    logger = logging.getLogger('errors')
    logger.error(f"Error in {context}: {str(error)}", exc_info=True) 