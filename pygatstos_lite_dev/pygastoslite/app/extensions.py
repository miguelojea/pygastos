from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


def init_extensions(app: Flask):
    db.init_app(app)
    with app.app_context():
        from app import models  # noqa: F401. NOTE: Important to import before db.create_all(), to create all tables
        #       of the models Also important to import here and not at the file beginning to avoid circular imports
        db.create_all()
