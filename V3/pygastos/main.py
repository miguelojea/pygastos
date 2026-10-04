import os
import logging
from datetime import datetime
import config.config as cfg
from libs.app_oop import FlaskApp
from libs.manage_db import DBHandler


def main():

    # Change the current working directory to the current file dir
    curr_file_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(curr_file_dir)

    # # Create output folders if they do not exist (when cloning, empty folders are not created)
    # for dir in cfg.NEEDED_PATHS:
    #     if not os.path.exists(dir):
    #         os.makedirs(dir)

    today = datetime.now().strftime('%y_%m_%d-%H.%M.%S')
    logging.basicConfig(
        level=cfg.LOGGING_LEVEL,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"static/logs/log_file_{today}.log", 'w', 'utf-8'),
            logging.StreamHandler()
        ]
    )

    flask_app = FlaskApp()
    flask_app.run(host='0.0.0.0', debug=False, port=8102)


if __name__ == '__main__':
    main()
