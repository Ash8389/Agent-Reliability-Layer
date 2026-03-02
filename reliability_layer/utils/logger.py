"""
Logger utility setup.
"""

import logging
from ..config import settings


def get_logger(name: str) -> logging.Logger:
    """Gets a logger with structured formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    logger.setLevel(settings.log_level.upper())
    return logger
