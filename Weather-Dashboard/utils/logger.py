import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging():
    """Configure logging with rotation and formatting"""
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    log_file = os.path.join(log_directory, "weather_app.log")

    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )

    console_handler = logging.StreamHandler()

    log_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    logger = logging.getLogger("WeatherDashboard")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
