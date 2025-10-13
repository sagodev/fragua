"""
fragua.core.logger
------------------
Lightweight logging wrapper for Fragua. Provides a configured logger
that other modules can import and use.
"""
import logging
from logging import Logger

def get_logger(name: str = "fragua", level: int = logging.INFO) -> Logger:
    """
    Return a configured logger with stream handler.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.propagate = False
    return logger

# module-level logger
logger = get_logger()
