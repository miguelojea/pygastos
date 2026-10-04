from datetime import time, timedelta
import secrets
from dataclasses import dataclass


@dataclass
class Config:
    SECRET_KEY = secrets.token_hex(32)  # Needed for the sessions to work. Any string is valid.
    # Sessions restart at each boot of the app
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(weeks=1)  # Equivalent to app.permanent_session_lifetime = timedelta(weeks=1)
    SESSION_REFRESH_EACH_REQUEST = False  # Equivalent to app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    BAN_TIME = 1  # in hours

    # If desired custom static and templates paths:
    # STATIC_FOLDER = '../static'
    # TEMPLATE_FOLDER = '../templates'
    # Then init the app with them:
    # app = Flask(
    #     __name__,
    #     static_folder=Config.STATIC_FOLDER,
    #     template_folder=Config.TEMPLATE_FOLDER
    # )


@dataclass
class DevConfig(Config):
    DEBUG = True


@dataclass
class ProdConfig(Config):
    DEBUG = False


@dataclass
class PeriodicConfig:
    """Configs of the periodic tasks."""
    # NOTE: None for all times. E.g. If sync_day = None, sync is done everyday.

    # DB backup
    db_backup_number = 20
    db_backup_day = None
    db_backup_day_of_week = 0  # 0 for monday
    db_backup_hour = 4
    # Sync
    sync_day = None
    sync_day_of_week = None
    sync_hour = 5
    # Log files
    log_files_when = "W0"  # W0 = Mondays (midnight if not atTime field). "s" for seconds.
    log_files_at_time = time(4, 0)   # time(4, 0) for 04:00 AM. None (default) for midnight
    log_files_interval = 1  # 1 for each time "when" occurs, 4 for 1 time each 4 "when" occurences...
    log_files_number = 10
