from datetime import date
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Entry
from typing import Tuple
from app.libs.logger import logger


class EntryService:

    @staticmethod
    def add_db_entry(wb_name: str, concept: str, value: float,
                     entry_date: date, description: str) -> Tuple[bool, str]:
        """Adds a new entry to the DB table.

        Returns:
            Tuple[bool, str]: Result, feedback msg.
        """
        try:
            new_entry = Entry(
                wb_name=wb_name,  # type: ignore
                concept=concept,  # type: ignore
                value=value,  # type: ignore
                entry_date=entry_date,  # type: ignore
                description=description  # type: ignore
            )
            db.session.add(new_entry)
            db.session.commit()
            msg = 'Entry added successfully.'
            logger.info(msg)
            return True, msg
        except AssertionError as e:
            db.session.rollback()
            msg = f'Validation failed: {e}.'
            logger.error(msg)
            return False, msg
        except IntegrityError:
            db.session.rollback()
            msg = 'Duplicated entry, not added.'
            logger.error(msg)
            return False, msg

    @staticmethod
    def parse_and_validate_web_entry_args(value: str, entry_date: str) -> Tuple[bool, dict, str]:
        """Parse and validate the entry arguments passed by HTML form, to add them to DB.

        Returns:
            Tuple[bool, dict, str]: Result, parsed args, feedback msg.
        """
        parsed_args = {}
        # value
        try:
            parsed_args['value'] = float(value.replace(',', '.'))
        except Exception:
            msg = f'Value ({value}) must be in float type format.'
            logger.error(msg)
            return False, {}, msg
        # entry_date
        try:
            parsed_args['entry_date'] = date.fromisoformat(entry_date)  # From YYYY-MM-DD to datetime.date
        except Exception:
            msg = f'Date ({entry_date}) must be in YYYY-MM-DD format.'
            logger.error(msg)
            return False, {}, msg
        # More validation/parsing not needed as HTML form ensures other data types
        msg = 'Entry args validated and parsed successsfully.'
        logger.info(msg)
        return True, parsed_args, msg

    @staticmethod
    def parse_and_validate_wb_entry_args():
        pass  # TODO: Use in Sync sequence

    @staticmethod
    def parse_and_validate_csv_entry_args():
        pass  # TODO: Use in upload_csv sequence if applies
