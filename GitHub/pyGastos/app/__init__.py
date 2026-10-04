from flask import Flask
from .extensions import init_extensions
from .routes import main, auth


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object('app.config.config.Config')  # TODO: Update to select ConfigDev, ConfigProd...

    init_extensions(app)  # Init extensions as SQLAlchemy, LoginManager...

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
