from app.extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import validates
from datetime import date


class Entry(db.Model):
    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key=True)
    wb_name = db.Column(db.String(32), nullable=False)  # E.g. "miguel", "comunes"
    concept = db.Column(db.String(64), nullable=False)
    value = db.Column(db.Numeric(8, 2), nullable=False)  # Until 999999.99
    entry_date = db.Column(db.Date, nullable=False)  # SQLite save date as text 'YYYY-MM-DD', SQLAlchemy formats it
    sync = db.Column(db.Boolean, default=False, nullable=False)  # True if DB value already updated to Google Sheets
    description = db.Column(db.String(64), default='', nullable=False)

    # UniqueConstraint that ensures there are not added repeated entries to the table.
    # If inserted: IntegrityError: UNIQUE constraint failed. TODO: Check and handle this error.
    __table_args__ = (
        UniqueConstraint(
            "wb_name",
            "concept",
            "value",
            "entry_date",
            "description",
            name="uq_entry_unique"
        ),
    )

    def __repr__(self):
        return f'<Entry {self.id}>'

    @validates('value')
    def validate_value(self, key, value):
        """Validates the value before adding it to the table."""
        assert (isinstance(value, int) or isinstance(value, float)), \
            f"The value ({value}) type ({type(value)}) must be int or float."
        assert value >= 0, f"The value ({value}) must be greater or equal than 0."
        return value

    @validates('entry_date')
    def validate_date(self, key, entry_date):
        """Validates the date before adding it to the table."""
        assert isinstance(entry_date, date), f"The date ({entry_date}) type ({type(entry_date)}) must be datetime.date."
        return entry_date

    # querys:
    # Entry.query.filter(Entry.entry_date >= date(2025, 8, 1))
    # Entry.query.filter_by(type="table1").all()
    # Entry.query.filter_by(type="table2").all()
