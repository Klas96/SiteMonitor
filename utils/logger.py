import logging
from pathlib import Path
import sys

def setup_logger(log_file='logs/application.log'):
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logging level

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler(sys.stdout)

    # Set level for handlers
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
