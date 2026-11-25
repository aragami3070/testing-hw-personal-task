"""Логирование без вывода учётных данных."""

import logging
import re
from pathlib import Path

from core.config import config


def mask(text: object) -> str:
    result = str(text)
    for secret in sorted((config.email, config.password), key=len, reverse=True):
        if secret:
            result = result.replace(secret, "[СКРЫТО]")
    result = re.sub(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", "[EMAIL СКРЫТ]", result)
    result = re.sub(r"(?<!\w)\+?\d[\d ()-]{8,}\d(?!\w)", "[ТЕЛЕФОН СКРЫТ]", result)
    return result


class MaskFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mask(record.getMessage())
        record.args = ()
        return True


def get_logger() -> logging.Logger:
    logger = logging.getLogger("ui_tests")
    if not logger.handlers:
        logger.setLevel(getattr(logging, config.log_level, logging.INFO))
        Path("logs").mkdir(exist_ok=True)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        for handler in (logging.StreamHandler(), logging.FileHandler("logs/test.log", encoding="utf-8")):
            handler.setFormatter(formatter)
            handler.addFilter(MaskFilter())
            logger.addHandler(handler)
        logger.propagate = False
    return logger


logger = get_logger()
