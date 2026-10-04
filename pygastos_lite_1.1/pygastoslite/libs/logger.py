import logging
import os

# Create logs folder if do not exist
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create log file
log_file = os.path.join(log_dir, 'log_file.log')

# Configure logger
logger = logging.getLogger('pygastos')
logger.setLevel(logging.INFO)

# Avoid duplicates if imported several times
if not logger.handlers:
    # Handler for the file
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # Handler for the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Add the same handlers to Flask logger (includes Werkzeug)
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.INFO)
for handler in logger.handlers:
    flask_logger.addHandler(handler)
