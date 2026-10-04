# Module to handle periodic tasks

# app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
# from apscheduler.triggers.date import DateTrigger
from app.libs.logger import logger
from datetime import datetime
# from datetime import timedelta
from app.libs.sync import Sync
from flask import Flask
from flask import current_app
from app.config.config import PeriodicConfig
import os
import shutil


def backup_db():
    # NOTE: This implementation assumes that the DB is not in use at the momment of the backup.
    #       If it can be in use, use API de SQLite

    logger.info(f"Executing scheduler task: Backup DB - {datetime.now()}")

    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    # Get backup files, order by name (date) and remove oldest until there are max of {PeriodicConfig.n_db_backups}
    files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir)]
    files.sort()
    while len(files) > PeriodicConfig.db_backup_number:
        old_file = files.pop(0)  # first is oldest
        os.remove(old_file)
        logger.info(f"Deleted: {old_file}.")

    # Create new backup file
    db_path = os.path.join("instance", "app.db")

    backup_path = os.path.join(
        backup_dir,
        f"backup_{datetime.now().date()}.db"
    )

    shutil.copy2(db_path, backup_path)

    logger.info(f"Backup created at {backup_path}.")


def sync_gsheets(app: Flask):
    with app.app_context():
        logger.info(f"Executing scheduler task: DB - Google Sheets Sync - {datetime.now()}")
        app = current_app._get_current_object()  # type: ignore . Use the context of the app inside the thread
        Sync.run_sync(app=app)


def start_scheduler(app: Flask):
    scheduler = BackgroundScheduler()

    # DB Backup
    # Sync DB - Google Sheets
    scheduler.add_job(
        backup_db,
        CronTrigger(
            day=PeriodicConfig.db_backup_day,
            day_of_week=PeriodicConfig.db_backup_day_of_week,
            hour=PeriodicConfig.db_backup_hour,
            minute=36
        )
    )

    # Sync DB - Google Sheets
    scheduler.add_job(
        sync_gsheets,
        CronTrigger(
            day=PeriodicConfig.sync_day,
            day_of_week=PeriodicConfig.sync_day_of_week,
            hour=PeriodicConfig.sync_hour
        ),
        args=[app]
    )

    # NOTE: DateTrigger for debugging
    # scheduler.add_job(
    #     sync_gsheets,
    #     DateTrigger(run_date=datetime.now() + timedelta(seconds=5)),
    #     args=[app],
    #     id="sync_gsheets_debug"
    # )

    scheduler.start()
    logger.info("Scheduler iniciado.")
