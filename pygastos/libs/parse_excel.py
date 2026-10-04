import pandas as pd
# import csv
import logging
import chardet

class Csv_Parser:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def detect_codification(self, filename: str) -> str:
        with open(filename, "rb") as f:
            result = chardet.detect(f.read())  # Detecta la codificación
            return result["encoding"]

    def convert_to_utf8(self, filename: str):
        encoding = self.detect_codification(filename=filename)
        # df = pd.read_csv(filename, encoding=encoding, delimiter=";")
        df = pd.read_csv(filename, encoding="ansi", delimiter=";")
        df.to_csv("converted_utf8.csv", encoding="utf-8", index=False, sep=";")


    def read_csv(self, filename: str) -> pd.DataFrame:
            try:
                df = pd.read_csv(filename, encoding='ansi', delimiter=';')
                return df
            # except FileNotFoundError:
            #     self._logger.error(f"Error: El archivo '{filename}' no existe.")
            #     return None
            # except pd.errors.EmptyDataError:
            #     self._logger.error("Error: El archivo está vacío.")
            #     return None
            # except pd.errors.ParserError:
            #     self._logger.error("Error: No se pudo parsear el archivo CSV.")
            #     return None
            except Exception as e:
                self._logger.error(e, exc_info=True)
                # self._logger.error(f"Error inesperado: {e}")
                return None


csv_parser = Csv_Parser()
data = csv_parser.detect_codification("files//Banca Electrónica - Movimientos Comunes.csv")
print(data)
data = csv_parser.convert_to_utf8("files//Banca Electrónica - Movimientos Comunes.csv")
data = csv_parser.read_csv("files//Banca Electrónica - Movimientos Comunes.csv")
if data is not None:
    print(data)
