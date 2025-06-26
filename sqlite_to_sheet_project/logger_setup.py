import logging
from sqlite_to_sheet_project.config import LOG_FILE_PATH

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
            logging.StreamHandler()
        ]
    )
