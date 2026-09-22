"""Logging setup for lab_fw."""

from __future__ import annotations

import logging


def setup_logging(level: str = "INFO") -> None:
    """Configure the lab_fw logger hierarchy once."""
    logger = logging.getLogger("lab_fw")
    logger.setLevel(level.upper())

    if logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )
    )
    logger.addHandler(handler)
    logger.propagate = False