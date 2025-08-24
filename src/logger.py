import os
import sys
import logging
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class InterceptHandler(logging.Handler):
    """Intercept standard logging messages toward loguru."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logger():
    """Configure loguru logger based on environment."""
    logger.remove()

    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_prod = environment == "production"

    config = {
        "level": "INFO" if is_prod else "DEBUG",
        "format": ("{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
                  if is_prod else
                  "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"),
        "serialize": is_prod,
        "colorize": not is_prod,
        "backtrace": not is_prod,
        "diagnose": not is_prod
    }

    logger.add(sys.stdout, **config)

    intercept_handler = InterceptHandler()
    logging.root.handlers = [intercept_handler]
    logging.root.setLevel(config["level"])

    # Intercept all existing and future loggers automatically
    for name in logging.root.manager.loggerDict.keys():
        logging_logger = logging.getLogger(name)
        logging_logger.handlers = [intercept_handler]
        logging_logger.propagate = False

    logger.info(f"Logger configured for {environment} environment with level {config['level']}")
    return logger

def get_logger():
    """Get the configured loguru logger instance."""
    return logger

setup_logger()
