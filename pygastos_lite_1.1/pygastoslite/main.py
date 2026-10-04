from libs.app import app
from libs.logger import logger


if __name__ == '__main__':
    logger.info("Init Flask app.")
    app.run(host='0.0.0.0', port=8101, debug=False)  # TODO: debug=True make it configurable.
    #       Add arg when launching main.py. E.g. python main.py --debug

    # debug=True:
    #   - Launches the server accesible from local network
    #   - Turns on debug mode
    #   - Activates automatic reload
