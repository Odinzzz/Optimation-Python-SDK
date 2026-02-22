from __future__ import annotations

import logging
from typing import Optional

_configured = False


def get_logger(name: str = "optimation", level: Optional[str] = None) -> logging.Logger:
    global _configured
    if not _configured:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        _configured = True

    logger = logging.getLogger(name)

    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    return logger
