# import os
import json5
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict, List
from gspread.spreadsheet import Spreadsheet
from gspread.worksheet import Worksheet
from libs.logger import logger
from datetime import datetime


class Workbook:
    def __init__(self, wb_name: str):

        self._wb_name = wb_name
        with open('config/common.json') as json_file:
            self._common_cfg = json5.load(json_file)

        self._col_concept: str = self._common_cfg['columns']['concept']
        self._col_val: str = self._common_cfg['columns']['value']
        self._col_desc: str = self._common_cfg['columns']['description']
        self._col_special_val: str = self._common_cfg['columns']['special_value']
        self._col_special_desc: str = self._common_cfg['columns']['special_description']
        self._row_first: int = self._common_cfg['rows']['first']
        self._row_last: int = self._common_cfg['rows']['last']

        self._months: List[str] = self._common_cfg['sheet_names']

        creds = Credentials.from_service_account_file(
            filename='private/credentials.json',
            scopes=self._common_cfg['scopes']
        )
        self._client = gspread.authorize(creds)

        with open('config/workbooks.json') as json_file:
            workbooks_cfg = json5.load(json_file)
        self._wb_cfg = workbooks_cfg[wb_name]
        self._wb: Spreadsheet = self._client.open_by_key(key=self._wb_cfg['id'])
        self._sheets: Dict[str, Worksheet] = {}
        self._load_sheets()
        self._concepts = [concept['name'] for concept in self._wb_cfg['concepts']]

        logger.info(f"{wb_name} Workbook Initialized.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._wb_name}>"

    def _load_sheets(self) -> None:
        # TODO: relave self._sheets[sheet.title] to common_cfg['sheet_names']
        for sheet in self._wb.worksheets():
            self._sheets[sheet.title] = sheet

    def add_entry(self, concept: str, value: str, description: Optional[str] = None,
                  sheet_name: Optional[str] = None) -> bool:
        """Adds a new entry to a workbook sheet.

        Args:
            concept (str): Concept of the entry. E.g. 'Ocio'
            value (str): Value of the entry. E.g. 12.34
            sheet_name (Optional[str], optional): Name of the sheet. E.g. 'Enero'. Defaults to None.
                If None, current month sheet will be used.
            description (Optional[str], optional): Description of the entry. Defaults to None.

        Returns:
            bool: result of the sequence.
        """

        if self._validate_args() is False:
            logger.error('Invalid args for new entry.')
            return False

        if sheet_name is None:
            sheet_name = self._months[datetime.now().month]

        sheet = self._sheets[sheet_name]

        is_special = self._is_special_concept(concept=concept)

        # Get first empty row
        first_empty_row = self._get_first_empty_row(sheet=sheet, is_special=is_special)
        if first_empty_row == -1:
            logger.error('No space for new entry.')
            return False

        # Update entry cells
        self._update_entry(sheet=sheet, row=first_empty_row, is_special=is_special, concept=concept, value=value,
                           description=description)

        return True

    def _is_special_concept(self, concept: str) -> bool:
        if concept == self._wb_cfg['special_conecpt']:
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
            col +
            str(self._row_first) +
            ':' +
            col +
            str(self._row_last)
        )  # E.g. 'P4:P35'

        # Check if there is empty row
        if ['-'] not in entries_concepts:
            return -1

        # Get new entry row
        first_empty_pos = entries_concepts.index(['-'])

        return self._row_first + first_empty_pos

    def _update_entry(self, sheet: Worksheet, row: int, is_special:bool, concept: Optional[str], value: Optional[str],
                      description: Optional[str]) -> None:

        # Update special entry cells (value and or description)
        if is_special is False:
            concept_col = self._col_concept
            value_col = self._col_val
            desc_col = self._col_desc
        else:
            concept_col = None
            value_col = self._col_special_val
            desc_col = self._col_special_desc
        if concept and concept_col:
            sheet.update_acell(label=f'{concept_col}{row}', value=concept)
        if value:
            sheet.update_acell(label=f'{value_col}{row}', value=value)
        if description:
            sheet.update_acell(label=f'{desc_col}{row}', value=description)

    def _validate_args(self) -> bool:
        return True  # TODO: implement


with open('config/common.json') as json_file:
    common_cfg = json5.load(json_file)

# wbs = {
#     'miguel': Workbook(wb_name='miguel')
# }
wbs = {}
def get_wb(name: str) -> Workbook:
    if name not in wbs:
        wbs[name] = Workbook(wb_name=name)
    return wbs[name]

