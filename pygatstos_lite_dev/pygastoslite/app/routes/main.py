from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from datetime import date
from sqlalchemy import text
from app.libs.logger import logger
from app.libs.sync import Sync, thread_running
from app.routes.auth import login_required
import json5
from datetime import datetime
import threading
from flask import current_app
import app.config.globals as glob
from collections import defaultdict
from io import StringIO
import csv
from app.libs.upload_csv import UploadCsv
from app.libs.db_handler import EntryService


main = Blueprint('main', __name__)
with open('app/config/workbooks.json') as json_file:
    workbooks_cfg: dict = json5.load(json_file)
wb_concepts = {}
for wb_name in workbooks_cfg.keys():
    wb_cfg = workbooks_cfg[wb_name]
    concepts = [concept['name'] for concept in wb_cfg['concepts']]
    wb_concepts[wb_name] = concepts

# Global variables for sync thread
start_sync_time = None

Upload_csv = UploadCsv()


@main.route('/')
@login_required
def index():
    return render_template('index.html')


@main.route('/add_entry', methods=['GET', 'POST'])
@login_required
def add_entry():
    if request.method == 'GET':
        today = date.today().isoformat()  # YYYY-MM-DD format, for <input type="date">
        return render_template(
            "add_entry.html",
            wb_concepts=wb_concepts,
            today=today)

    # Get parameters
    wb_name = request.form['wb_name']
    concept = request.form['concept']
    value = request.form['value']
    entry_date = request.form['date']
    description = request.form['description']
    logger.info(f'Add entry requested: Workbook: {wb_name}, Concept: {concept}, Value: {value}, '
                f'Date: {entry_date}, Description: {description}.')

    # Parse and validate parameters
    res, args, msg = EntryService.parse_and_validate_web_entry_args(value=value, entry_date=entry_date)
    if res is False:
        flash(msg, "error")
        return redirect(url_for('main.add_entry'))
    value = args['value']
    entry_date = args['entry_date']

    # Add entry to DB
    res, msg = EntryService.add_db_entry(
        wb_name=wb_name, concept=concept, value=value, entry_date=entry_date, description=description)
    if res is False:
        flash(msg, "error")
        return redirect(url_for('main.add_entry'))

    flash(msg, "success")
    return redirect(url_for('main.add_entry'))


@main.route('/tables')
@login_required
def tables():
    # Get DB table
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    if len(tables) != 1:
        raise ValueError(f"Only 1 table is expected at DB, but there are {len(tables)} tables.")
    table = tables[0]

    # Get column names. PRAGMA SQLite command gets metadata
    columns = db.session.execute(text(f"PRAGMA table_info({table})")).fetchall()
    column_names = [col[1] for col in columns]

    # Get all table registers
    result = db.session.execute(text(f"SELECT * FROM {table}")).fetchall()

    # Full Table
    table_data = {"complete": {"columns": column_names, "rows": result}}

    # Hierarchical grouping: wb_name → year → month
    # Creates Dict of Dict of Dict of Lists.
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for row in result:
        # Convert column names and row lists into dict
        row_dict = dict(zip(column_names, row))
        # Get grouping keys, to know in which group to add the dict
        wb_name = row_dict["wb_name"]
        entry_date = datetime.strptime(str(row_dict["entry_date"]), "%Y-%m-%d")
        year = entry_date.strftime("%Y")
        month = entry_date.strftime("%m")
        # Add the dict to the corresponding group
        grouped[wb_name][year][month].append(row)  # E.g. grouped["miguel"]["2025"]["08"].append(row)

    return render_template(
        "tables.html",
        table_data=table_data,
        grouped=grouped,
        columns=column_names
    )


@main.route('/sync', methods=['GET', 'POST'])
@login_required
def sync():
    global start_sync_time

    if request.method == 'GET':
        elapsed = None
        if thread_running.is_set() is True and start_sync_time is not None:
            elapsed = datetime.now() - start_sync_time

        return render_template(
            'sync.html',
            thread_running=thread_running.is_set(),
            elapsed=elapsed,
            last_sync_time=glob.last_sync_time
        )

    logger.info('Sync requested.')
    if thread_running.is_set() is True:
        msg = 'A sync routine is already in progress.'
        logger.warning(msg)
        flash(msg, "warning")
    else:
        start_sync_time = datetime.now()
        app = current_app._get_current_object()  # type: ignore . Use the context of the app inside the thread
        sync_thread = threading.Thread(target=Sync.run_sync, args=(app, ))
        sync_thread.start()
        msg = 'Sync routine started.'
        logger.info(msg)
        flash(msg, "success")
    return redirect(url_for('main.sync'))


@main.route('/upload_csv', methods=['GET', 'POST'])
@login_required
def upload_csv():
    """Upload CSV with entries to add to DB"""

    wb_names = list(workbooks_cfg.keys())

    if request.method == 'GET':
        return render_template(
            'upload_csv.html',
            wb_names=wb_names
        )

    logger.info('Upload CSV requested.')

    uploaded_data = {}

    for wb in wb_names:
        for csv_type in ["cc", "card"]:  # Cuenta Corriente, Tarjeta
            field_name = f"{wb}_{csv_type}"
            file = request.files.get(field_name)

            if file and file.filename:  # If there is file
                content = file.read().decode("cp1252")  # or "latin-1". Not utf-8.
                reader = csv.reader(StringIO(content), delimiter=';')
                rows = list(reader)
                uploaded_data[field_name] = rows

    if not uploaded_data:
        flash("No CSV file was uploaded.", "warning")
        return redirect(url_for("main.upload_csv"))

    logger.info(f"Received CSV files: {uploaded_data.keys()}")
    ret = Upload_csv.upload_csv_data(data=uploaded_data)
    if ret is False:
        msg = "Failed to process and upload CSV files to DB."
        logger.error(msg)
        flash(msg, "error")
    else:
        msg = "CSV files proccessed successfully and added to DB."
        logger.info(msg)
        flash(msg, "success")
    return redirect(url_for("main.upload_csv"))
