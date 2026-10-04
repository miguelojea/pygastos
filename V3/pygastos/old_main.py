#! C:\Users\migue\OneDrive\Documentos\Proyectos\Gastos\pygastos\env\Scripts\python.exe
from config import config as cfg
from libs.manage_db import DBHandler


# Needed to add path to use hupper
# import sys
import os
# Change the current working directory to the current file dir
curr_file_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_file_dir)
import logging  # noqa: E402
def main() -> None:

    # sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("log_file.log", 'w', 'utf-8'),
            logging.StreamHandler()
        ]
    )

    # db_handler = DBHandler()
    # print(db_handler._tables)
    # print(db_handler._tables['personal']._concepts)

    pass



if __name__ == "__main__":
    main()
