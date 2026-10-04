# import os
import json5
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict, List
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from app.libs.logger import logger
from datetime import date
import time


class Workbook:
    def __init__(self, wb_name: str):

        self._wb_name = wb_name
        with open('app/config/common.json') as json_file:
            self._common_cfg = json5.load(json_file)

        self._col_concept: str = self._common_cfg['columns']['concept']
        self._col_val: str = self._common_cfg['columns']['value']
        self._col_desc: str = self._common_cfg['columns']['description']
        self._col_date: str = self._common_cfg['columns']['date']
        self._col_special_val: str = self._common_cfg['columns']['special_value']
        self._col_special_date: str = self._common_cfg['columns']['special_date']
        self._col_special_desc: str = self._common_cfg['columns']['special_description']
        self._row_first: int = self._common_cfg['rows']['first']
        self._row_last: int = self._common_cfg['rows']['last']

        self._months: List[str] = self._common_cfg['months']

        creds = Credentials.from_service_account_file(
            filename='private/credentials.json',
            scopes=self._common_cfg['scopes']
        )
        self._client = gspread.authorize(creds)

        with open('app/config/workbooks.json') as json_file:
            workbooks_cfg = json5.load(json_file)
        self._wb_cfg = workbooks_cfg[wb_name]
        self._wb: Spreadsheet = self._client.open_by_key(key=self._wb_cfg['id'])
        self._sheets: Dict[str, Worksheet] = {}
        self._load_sheets()
        self._concepts = [concept['name'] for concept in self._wb_cfg['concepts']]
        self._special_concept = self._wb_cfg['special_concept']

        logger.info(f"{wb_name} Workbook Initialized.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._wb_name}>"

    @property
    def special_concept(self) -> str:
        return self._special_concept

    def _load_sheets(self) -> None:
        for sheet in self._wb.worksheets():
            self._sheets[sheet.title] = sheet

    def get_sheet_entries(self, sheet: Worksheet, special: bool) -> List[List[str]]:
        if special is False:
            # Get normal entries
            sheet_normal_entries = sheet.get(
                self._col_concept
                + str(self._row_first)
                + ':'
                + self._col_desc
                + str(self._row_last)
            )  # E.g. 'P4:P35'
            time.sleep(1)  # Wait 1s to not exceed Google Sheets API limit. TODO: Update to reduce API calls
            # Remove rows with concept == '-'
            sheet_normal_entries_filtered = [row for row in sheet_normal_entries if row[0] != '-']
            # Format: [['Ocio', 'Gasto', '1,23 €', '1/1/2025', 'abc'], ...]
            return sheet_normal_entries_filtered
        # Get special entries
        sheet_special_entries = sheet.get(
            self._col_special_val
            + str(self._row_first)
            + ':'
            + self._col_special_desc
            + str(self._row_last)
        )  # E.g. 'P4:P35'
        time.sleep(1)  # Wait 1s to not exceed Google Sheets API limit. TODO: Update to reduce API calls
        # Remove rows with concept == '-'
        sheet_special_entries_filtered = [row for row in sheet_special_entries if row[0] != '-']
        # Format: [['1,23 €', '1/1/2025', 'abc'], ...]
        return sheet_special_entries_filtered

    def add_wb_entry(self, concept: str, value: float, description: Optional[str] = None,
                     entry_date: Optional[date] = None) -> bool:
        """Adds a new entry to a workbook sheet.

        Args:
            concept (str): Concept of the entry. E.g. 'Ocio'
            value (str): Value of the entry. E.g. 12.34
            entry_date (Optional[date], optional): Date of the entry. Defaults to None.
                If None, current date will be used.
            description (Optional[str], optional): Description of the entry. Defaults to None.

        Returns:
            bool: result of the sequence.
        """

        if self._validate_args() is False:
            logger.error('Invalid args for new entry.')
            return False

        if entry_date is None:
            entry_date = date.today()

        sheet_name = self._months[entry_date.month - 1]
        sheet = self._sheets[sheet_name]

        is_special = self._is_special_concept(concept=concept)

        # Get first empty row
        first_empty_row = self._get_first_empty_row(sheet=sheet, is_special=is_special)
        if first_empty_row == -1:
            logger.error('No space for new entry.')
            return False

        # Update entry cells
        self._update_entry(sheet=sheet, row=first_empty_row, is_special=is_special, concept=concept, value=value,
                           entry_date=entry_date, description=description)

        return True

    def _is_special_concept(self, concept: str) -> bool:
        if concept == self._special_concept:
            return True
        return False

    def _get_first_empty_row(self, sheet: Worksheet, is_special: bool) -> int:
        """Returns entry row or -1 if there is not entry row."""
        # Get entries
        if is_special is True:
            col = self._col_special_val
        else:
            col = self._col_concept

        entries_concepts = sheet.get(
            col
            + str(self._row_first)
            + ':'
            + col
            + str(self._row_last)
        )  # E.g. 'P4:P35'
        time.sleep(1)  # Wait 1s to not exceed Google Sheets API limit. TODO: Update to reduce API calls

        # Check if there is empty row
        if ['-'] not in entries_concepts:
            return -1

        # Get new entry row
        first_empty_pos = entries_concepts.index(['-'])

        return self._row_first + first_empty_pos

    def _update_entry(self, sheet: Worksheet, row: int, is_special: bool, concept: Optional[str],
                      value: Optional[float], entry_date: Optional[date], description: Optional[str]) -> None:

        # Update special entry cells (value and or description)
        if is_special is False:
            col_concept = self._col_concept
            col_value = self._col_val
            col_date = self._col_date
            col_desc = self._col_desc
        else:
            col_concept = None
            col_value = self._col_special_val
            col_date = self._col_special_date
            col_desc = self._col_special_desc
        if concept and col_concept:
            sheet.update_acell(label=f'{col_concept}{row}', value=concept)
            time.sleep(1)  # Wait 1s to not exceed Google Sheets API limit. TODO: sheet.update(rango, data) instead
        if value:
            sheet.update_acell(label=f'{col_value}{row}', value=value)
            time.sleep(1)
        if entry_date:
            sheet.update_acell(label=f'{col_date}{row}', value=entry_date.strftime("%d/%m/%Y"))
            time.sleep(1)
        if description:
            sheet.update_acell(label=f'{col_desc}{row}', value=description)
            time.sleep(1)
        logger.info(f'WB entry updated. wb: {self._wb_name}; concept: {concept}; value: {value}; '
                    f'entry_date: {entry_date}; description: {description}.')

    def _validate_args(self) -> bool:
        return True  # TODO: implement


with open('app/config/common.json') as json_file:
    common_cfg = json5.load(json_file)
wbs = {}


def get_wb(name: str) -> Workbook:
    if name not in wbs:
        wbs[name] = Workbook(wb_name=name)
    return wbs[name]
