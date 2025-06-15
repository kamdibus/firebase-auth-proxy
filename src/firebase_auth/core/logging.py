import sys

from loguru import logger


def setup_logging(log_level: str = 'INFO'):
    logger.remove()

    logger.add(
        sys.stdout,
        level=log_level,
        format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>',
        colorize=True,
    )

    logger.add(
        'logs/auth-service.log',
        level=log_level,
        format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}',
        rotation='100 MB',
        retention='30 days',
    )


def get_logger(name: str):
    return logger.bind(name=name)
