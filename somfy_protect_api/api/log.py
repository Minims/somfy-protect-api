"""Utils Package"""

import logging
import logging.handlers

LOGGER = logging.getLogger(__name__)


def setup_logger(debug: bool = False) -> None:
    """Setup Logging

    Args:
        debug (bool, optional): True if debug enabled. Defaults to False.
    """
    if debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")
    LOGGER.addHandler(logging.StreamHandler())
