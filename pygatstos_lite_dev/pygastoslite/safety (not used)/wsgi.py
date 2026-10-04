from app import create_app
from app.libs.logger import logger
from app.libs.scheduler import start_scheduler

app = create_app()
logger.info("Flask app created.")

# Start periodic tasks
start_scheduler(app)
