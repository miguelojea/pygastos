# Sync DB and Google Sheets
import json5
from app.libs.workbook import get_wb
from app.extensions import db
from datetime import date, datetime
from app.models import Entry
from typing import List, Tuple
import threading
from flask import Flask
import app.config.globals as glob
from app.libs.logger import logger

thread_running = threading.Event()


class Sync:
    """Class to sync DB and Google Sheets"""
    with open('app/config/workbooks.json') as json_file:
        workbooks_cfg = json5.load(json_file)
    with open('app/config/common.json') as json_file:
        common_cfg = json5.load(json_file)
    _wb_names: List[str] = list(workbooks_cfg.keys())
    _months: List[str] = common_cfg['months']

    @classmethod
    def run_sync(cls, app: Flask):
        thread_running.set()
        logger.info('Sync thread started.')
        try:
            with app.app_context():  # Use the context of the app inside the thread
                cls.sync_all()
        finally:
            # This executes even if any Exception raises in the try.
            thread_running.clear()
            glob.last_sync_time = datetime.now()
            logger.info('Sync thread ended.')

    @classmethod
    def sync_all(cls):

        # TODO: Check Google Sheets has not repeated entries

        # TODO: Measure time of sync sequence.

        # TODO: Order Google sheets entries by date (remove and add all in order)

        # For all months (sheets):
        # 1.1 Add entries from DB with sync = False to Google Sheets.
        # 1.2 Remove entries form DB that are not at Google Sheets.
        # 2. Add entries from Google Sheets that are not at DB to DB

        for wb_name in cls._wb_names:

            for month in cls._months:
                # Uncomment this to sync only 1 month.
                # n_month = cls._months.index(month)
                # if n_month != 7:
                #     continue
                cls._sync_month(wb_name=wb_name, month=month)
            # return  # TODO: remove this: only first WB.

    @classmethod
    def _sync_month(cls, wb_name: str, month: str):

        # 1.1. Add entries from DB with sync = False to Google Sheets
        # 1.2. Remove entries form DB that are not at Google Sheets
        cls._sync_month_from_db(wb_name=wb_name, month=month)

        # 2. Add entries from Google Sheets that are not at DB
        cls._sync_month_from_sheet(wb_name=wb_name, month=month)

    @classmethod
    def _sync_month_from_db(cls, wb_name: str, month: str):
        # 1.1. Add entries from DB with sync = False to Google Sheets
        # 1.2. Remove entries form DB that are not at Google Sheets

        wb = get_wb(name=wb_name)
        n_month = cls._months.index(month) + 1

        # Get and refactor (to have DB format) Sheet entries (normal and special)
        sheet_normal_entries, sheet_special_entries = cls._get_sheet_refactored_entries(wb_name=wb_name, month=month)

        # TODO: Check there are not repeated entries in Sheet (normal and special)
        # TODO: Check that all the entries of the Sheet have a entry_date that matches the Sheet month.

        # Get DB entries
        start_date = date(date.today().year, n_month, 1)
        if n_month == 12:
            end_date = date(date.today().year + 1, 1, 1)
        else:
            end_date = date(date.today().year, n_month + 1, 1)
        db_entries: List[Entry] = Entry.query.filter(
            Entry.wb_name == wb_name,
            Entry.entry_date >= start_date,
            Entry.entry_date < end_date  # not included
        ).all()

        # Add DB entries with sync = False to Sheet and update sync = True
        for db_entry in db_entries:

            # Check db_entry date is in expected month
            if db_entry.entry_date.month != n_month:
                raise Exception(f'Entry month {db_entry.entry_date.month} and expected month {n_month} do not match.')

            if db_entry.sync is False:
                # 1.1. Add entries from DB with sync = False to Google Sheets.

                # Check db_entry with sync == False is not already at Sheet. Error if it is
                if wb._is_special_concept(db_entry.concept) is False:
                    # Normal entry
                    for sheet_entry in sheet_normal_entries:
                        if sheet_entry[0] == db_entry.concept and\
                                sheet_entry[2] == float(db_entry.value) and\
                                sheet_entry[3] == db_entry.entry_date and\
                                sheet_entry[4] == db_entry.description:
                            raise Exception(
                                'There should not be a DB entry with sync = False that already is at Sheets.')
                else:
                    # Special entry
                    for sheet_entry in sheet_special_entries:
                        if sheet_entry[0] == float(db_entry.value) and\
                                sheet_entry[1] == db_entry.entry_date and\
                                sheet_entry[2] == db_entry.description:
                            raise Exception(
                                'There should not be a DB entry with sync = False that already is at Sheets.')

                # Add the DB entry to the Sheet
                wb.add_wb_entry(
                    concept=db_entry.concept,
                    value=float(db_entry.value),
                    entry_date=db_entry.entry_date,
                    description=db_entry.description
                )

                # Update DB entry sync field to True
                db_entry.sync = True

            else:
                # 1.2. Remove entries form DB that are not at Google Sheets

                # Check if normal entry at sheet. Remove from DB if not.
                if wb._is_special_concept(db_entry.concept) is False:
                    # Normal entry
                    for sheet_entry in sheet_normal_entries:
                        if sheet_entry[0] == db_entry.concept and\
                                sheet_entry[2] == float(db_entry.value) and\
                                sheet_entry[3] == db_entry.entry_date and\
                                sheet_entry[4] == db_entry.description:
                            break
                    else:
                        # Entry not at Google Sheets, remove it
                        db.session.delete(db_entry)
                else:
                    # Special entry
                    for sheet_entry in sheet_special_entries:
                        if sheet_entry[0] == float(db_entry.value) and\
                                sheet_entry[1] == db_entry.entry_date and\
                                sheet_entry[2] == db_entry.description:
                            break
                    else:
                        # Entry not at Google Sheets, remove it
                        db.session.delete(db_entry)

        # Commit the DB changes
        db.session.commit()

        # Check there is not DB entry with sync = False
        db_entries = Entry.query.filter(
            Entry.wb_name == wb_name,
            Entry.entry_date >= start_date,
            Entry.entry_date < end_date,  # not included
            Entry.sync == False,  # noqa: E712
        ).all()
        if db_entries:
            raise Exception('There should not be DB entries with sync = True after sync first step, but there are.')

    @classmethod
    def _sync_month_from_sheet(cls, wb_name: str, month: str):
        # 2. Add entries from Google Sheets that are not at DB (added manually)

        wb = get_wb(name=wb_name)

        # Get and refactor (to have DB format) Sheet entries (normal and special)
        sheet_normal_entries, sheet_special_entries = cls._get_sheet_refactored_entries(wb_name=wb_name, month=month)

        # Add Normal entries from Sheet to DB
        for entry in sheet_normal_entries:
            # Continue if the entry is the Special entries sum
            if wb._is_special_concept(entry[0]) is True:
                continue
            # Get parameters
            concept = entry[0]
            value = entry[2]
            entry_date = entry[3]
            description = entry[4]

            # Check the sheet entry is not already at the DB
            entry_already_in_db = cls._is_entry_already_in_db(
                wb_name=wb_name, concept=concept, value=value, entry_date=entry_date, description=description)
            if entry_already_in_db is True:
                continue

            # Add entry to DB
            new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                description=description, sync=True)  # type: ignore
            db.session.add(new_entry)

        # Add Special entries from Sheet to DB
        for entry in sheet_special_entries:
            # Get parameters
            concept = wb.special_concept
            value = entry[0]
            entry_date = entry[1]
            description = entry[2]

            # Check the sheet entry is not already at the DB
            entry_already_in_db = cls._is_entry_already_in_db(
                wb_name=wb_name, concept=concept, value=value, entry_date=entry_date, description=description)
            if entry_already_in_db is True:
                continue

            # Add entry to DB
            new_entry = Entry(  # TODO: Use EntryService.add_entry instead.
                wb_name=wb_name, concept=concept, value=value, entry_date=entry_date,  # type: ignore
                description=description, sync=True)  # type: ignore
            db.session.add(new_entry)

        # Commit the new entries
        db.session.commit()

    @classmethod
    def _get_sheet_refactored_entries(cls, wb_name: str, month: str) -> Tuple[list, list]:
        """Get and refactor (to have DB format) Sheet entries (normal and special)."""

        wb = get_wb(name=wb_name)

        # Get sheet_normal_entries
        sheet_normal_entries = wb.get_sheet_entries(sheet=wb._sheets[month], special=False)
        # format: ['Ocio', 'Gasto', '1,23 €', '1/1/2026', 'abc']  # TODO: parametrize

        # TODO: Add entry in 1 action to reduce time.

        # Refactor sheet_normal_entries
        for entry in sheet_normal_entries:
            if entry[0] == '-' or wb._is_special_concept(entry[0]) is True:
                continue
            entry[2] = entry[2].replace('.', '')
            entry[2] = entry[2].replace(',', '.')
            entry[2] = entry[2].replace(' €', '')
            entry[2] = float(entry[2])  # type: ignore
            entry[3] = datetime.strptime(entry[3], "%d/%m/%y").date()  # type: ignore
            entry[4] = '' if entry[4] == '-' else entry[4]
        # format: ['Ocio', 'Gasto', '1.23', 'datetime.date(...)', '-']

        # Get sheet_special_entries
        sheet_special_entries = wb.get_sheet_entries(sheet=wb._sheets[month], special=True)
        # format: ['1,23 €', '1/1/2026', 'abc']  # TODO: parametrize

        # Refactor sheet_special_entries
        for entry in sheet_special_entries:
            if entry[0] == '-':
                continue
            entry[0] = entry[0].replace('.', '')
            entry[0] = entry[0].replace(',', '.')
            entry[0] = entry[0].replace(' €', '')
            entry[0] = float(entry[0])  # type: ignore
            entry[1] = datetime.strptime(entry[1], "%d/%m/%y").date()  # type: ignore
            entry[2] = '' if entry[2] == '-' else entry[2]
        # format: ['1.23', 'datetime.date(...)', '-']

        return (sheet_normal_entries, sheet_special_entries)

    @classmethod
    def _is_entry_already_in_db(
            cls, wb_name: str, concept: str, value: float, entry_date: date, description: str) -> bool:
        db_entry = Entry.query.filter(
            Entry.wb_name == wb_name,
            Entry.concept == concept,
            Entry.value == value,
            Entry.entry_date == entry_date,
            Entry.description == description
        ).one_or_none()
        # TODO: Check MultipleResultsFound Exception is raised if more than 1 result found
        if db_entry is None:
            return False
        return True
