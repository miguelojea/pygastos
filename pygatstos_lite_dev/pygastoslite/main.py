from app import create_app
from app.libs.logger import logger
from app.libs.scheduler import start_scheduler


if __name__ == '__main__':
    app = create_app()
    logger.info("Flask app created.")

    # Start periodic tasks
    start_scheduler(app)

    # Start Flask app
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8101, debug=False)
