from typing import Dict, List
import json5
from datetime import datetime
from app.libs.logger import logger
from app.models import Entry
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class UploadCsv:
    def __init__(self):

        with open('app/config/workbooks.json') as json_file:
            workbooks_cfg: dict = json5.load(json_file)
        self._csv_configs: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        self._wb_names = list(workbooks_cfg.keys())
        for wb_name in workbooks_cfg.keys():
            self._csv_configs[wb_name] = workbooks_cfg[wb_name]['csv']

        self._cc_col_date = 1
        self._cc_col_value = 3
        self._cc_col_description = 2
        self._cc_col_description_2 = 7

        self._card_col_date = 1
        self._card_col_value = 5
        self._card_col_description = 4

        # TODO: Custom the description instead of copy from CSV.
        # E.g. Naturgy instead of 000000981808 NATURGY CLIENTES, S.A.
        # TODO: Hous expenses (water, electricity...): Move to the corresponding month
        #       (and split in several months if apply)

    def upload_csv_data(self, data: Dict[str, List[List[str]]]) -> bool:
        """Upload CSV contents to DB"""
        """data format example:
        {
            'comunes_cc': [
                ['Fecha ctble', 'Fecha valor', 'Concepto', 'Importe', 'Moneda', 'Saldo', 'Moneda', 'Concepto ampliado'],
                ['26-06-2025', '26-06-2025', 'CTAG', '1551,09', 'EUR', '4566,19', 'EUR', 'ABONO NOMINA 06/2025'],
                ['26-06-2025', '26-06-2025', 'MIGUEL JULIO', '-600,00', 'EUR', '3966,19', 'EUR', 'MIGUEL JULIO'],
                ...
            ],
            'miguel_card': [
                ['', 'F.OPERAC.', 'TIPO OPERACIÓN', 'SITUACIÓN', 'CONCEPTO', 'IMPORTE', 'F.PAGO'],
                ['TIT.', '12/07/25', 'FRA. VENTA', 'Liquidado', 'LA MAFIA \\VILLAGARCIA', '-90,20 EUR', 'Fin de mes'],
                ['TIT.', '15/07/25', 'FRA. VENTA', 'Liquidado', 'GANDARA ARTESANOS \\VI', '-1,87 EUR', 'Fin de mes'],
                ...
            ],
            ...
        }"""

        for name, csv_data in data.items():
            wb_name = name.removesuffix('_cc').removesuffix('_card')
            if wb_name not in self._wb_names:
                raise Exception(f'CSV read {name} not in configured workbooks ({self._wb_names}).')
            if '_cc' in name:
                self._upload_cc_csv(wb_name=wb_name, csv_data=csv_data)
            elif '_card' in name:
                self._upload_card_csv(wb_name=wb_name, csv_data=csv_data)
            else:
                raise Exception(f'Invalid CSV name at HTML: {name}. It must have "_cc" or "_card" in the name.')

        return True  # TODO: Sync to add all new DB entries to Google Sheets.

    def _upload_cc_csv(self, wb_name: str, csv_data: List[List[str]]):
        csv_config = self._csv_configs[wb_name]['cc']
        for entry in csv_data[1:]:
            entry_found = False

            for wb_concept, concept_substrings in csv_config.items():
                for concept_substring in concept_substrings:
                    if concept_substring in entry[self._cc_col_description]:
                        if wb_concept == 'Ignore':
                            entry_found = True
                            break

                        # Get parameters
                        entry_found = True
                        concept = wb_concept
                        value = entry[self._cc_col_value]  # Format: '-600,23'
                        entry_date = entry[self._cc_col_date]  # Format: '26-06-2025'
                        description = entry[self._cc_col_description]  # Format MIGUEL JULIO

                        # Process parameters
                        value = abs(float(value.replace(',', '.')))
                        entry_date = datetime.strptime(entry_date, "%d-%m-%Y")
                        description = description.title()
                        logger.info(f'New entry requested: Workbook: {wb_name}, Concept: {concept}, Value: {value}, '
                                    f'Date: {entry_date}, Description: {description}.')

                        # Add entry to DB
                        new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                            wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                            description=description)  # type: ignore
                        try:
                            # db.session.add(new_entry)
                            db.session.merge(new_entry)  # merge only add if not exist entry
                            db.session.commit()
                            logger.info(f'{new_entry} entry added.')
                            # return 'Entry added.'
                        except AssertionError as e:
                            logger.error(f'Failed to add entry: {e}')
                            raise Exception(e)
                        except IntegrityError as e:
                            db.session.rollback()  # Return to previous session state to clean it and avoid error
                            logger.warning(f'Duplicated entry, not added. {e}')
                if entry_found is True:
                    break
            else:
                # Entry not found at config, adding with Unknown concept
                concept = 'Desconocido'
                value = entry[self._cc_col_value]  # Format: '-600,23'
                entry_date = entry[self._cc_col_date]  # Format: '26-06-2025'
                description = entry[self._cc_col_description]  # Format MIGUEL JULIO

                # Process parameters
                value = abs(float(value.replace(',', '.')))
                entry_date = datetime.strptime(entry_date, "%d-%m-%Y")
                description = description.title()
                logger.info(f'New entry requested: Workbook: {wb_name}, Concept: {concept}, Value: {value}, '
                            f'Date: {entry_date}, Description: {description}.')

                # Add entry to DB
                new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                    wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                    description=description)  # type: ignore
                try:
                    db.session.add(new_entry)
                    db.session.commit()
                    logger.info(f'{new_entry} entry added.')
                    # return 'Entry added.'
                except AssertionError as e:
                    logger.error(f'Failed to add entry: {e}')
                    raise Exception(e)
                except IntegrityError as e:
                    db.session.rollback()  # Return to previous session state to clean it and avoid error
                    logger.warning(f'Duplicated entry, not added. {e}')

    def _upload_card_csv(self, wb_name: str, csv_data: List[List[str]]):
        csv_config = self._csv_configs[wb_name]['card']
        for entry in csv_data[1:]:
            entry_found = False

            for wb_concept, concept_substrings in csv_config.items():
                for concept_substring in concept_substrings:
                    if concept_substring in entry[self._card_col_description]:
                        if wb_concept == 'Ignore':
                            entry_found = True
                            break

                        # Get parameters
                        entry_found = True
                        concept = wb_concept
                        value = entry[self._card_col_value]  # Format: '-600,23'
                        entry_date = entry[self._card_col_date]  # Format: '26-06-2025'
                        description = entry[self._card_col_description]  # Format MIGUEL JULIO

                        # Process parameters
                        value = float(value.replace(',', '.').replace(' EUR', ''))
                        if wb_concept == 'Gasolina' and value < 0:
                            entry_found = True  # Gasoline return
                            break
                        value = abs(value)
                        entry_date = datetime.strptime(entry_date, "%d/%m/%y")
                        description = description.title()
                        logger.info(f'New entry requested: Workbook: {wb_name}, Concept: {concept}, Value: {value}, '
                                    f'Date: {entry_date}, Description: {description}.')

                        # Add entry to DB
                        new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                            wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                            description=description)  # type: ignore
                        try:
                            # db.session.add(new_entry)
                            db.session.merge(new_entry)  # merge only add if not exist entry
                            db.session.commit()
                            logger.info(f'{new_entry} entry added.')
                            # return 'Entry added.'
                        except AssertionError as e:
                            logger.error(f'Failed to add entry: {e}')
                            raise Exception(e)
                        except IntegrityError as e:
                            db.session.rollback()  # Return to previous session state to clean it and avoid error
                            logger.warning(f'Duplicated entry, not added. {e}')
                if entry_found is True:
                    break
            else:
                # Entry not found at config, adding with Unknown concept
                concept = 'Desconocido'
                value = entry[self._card_col_value]  # Format: '-600,23'
                entry_date = entry[self._card_col_date]  # Format: '26-06-2025'
                description = entry[self._card_col_description]  # Format MIGUEL JULIO

                # Process parameters
                value = abs(float(value.replace(',', '.').replace(' EUR', '')))
                entry_date = datetime.strptime(entry_date, "%d/%m/%y")
                description = description.title()
                logger.info(f'New entry requested: Workbook: {wb_name}, Concept: {concept}, Value: {value}, '
                            f'Date: {entry_date}, Description: {description}.')

                # Add entry to DB
                new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                    wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                    description=description)  # type: ignore
                try:
                    db.session.add(new_entry)
                    db.session.commit()
                    logger.info(f'{new_entry} entry added.')
                    # return 'Entry added.'
                except AssertionError as e:
                    logger.error(f'Failed to add entry: {e}')
                    raise Exception(e)
                except IntegrityError as e:
                    db.session.rollback()  # Return to previous session state to clean it and avoid error
                    logger.warning(f'Duplicated entry, not added. {e}')
