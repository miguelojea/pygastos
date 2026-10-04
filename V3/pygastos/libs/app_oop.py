#! C:\Users\migue\OneDrive\Documentos\Proyectos\SleePy\sleepy\env\Scripts\python.exe

import os
import logging
from flask import Flask, request, render_template, jsonify
import config.config as cfg
from datetime import datetime
from typing import List, Dict


class FlaskApp():

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._app = Flask(__name__, template_folder='../templates', static_folder='../static')

        # Configurar nivel de logging para Flask
        self._app.logger.setLevel(cfg.LOGGING_LEVEL)
        # Deshabilitar el logging de Werkzeug (que maneja las peticiones HTTP)
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(cfg.HTTP_LOGGING_LEVEL)
        # # Opcional: Si hay algún manejador de logs heredado, removerlo
        # for handler in werkzeug_logger.handlers:
        #     werkzeug_logger.removeHandler(handler)

        self._logger.info('App starts.')

        # Ruta de la carpeta de audios
        self._audio_folder = os.path.join(self._app.static_folder, 'audios')
        self._init_time = datetime.now()
        self._register_endpoints()

        # DataBases
        # TODO:

    def _register_endpoints(self) -> None:
        self._app.add_url_rule(rule='/', view_func=self._index)
        self._app.add_url_rule(rule='/api/home', view_func=self._home, methods=['GET', 'POST'])
        self._app.add_url_rule(rule='/api/add_entry', view_func=self._add_entry, methods=['GET'])
        self._app.add_url_rule(rule='/api/submit_entry', view_func=self._submit_entry, methods=['POST'])

    def run(self, *args, **kwargs):
        self._app.run(*args, **kwargs)

    def _index(self) -> str:
        return render_template('index.html')

    def _home(self) -> str:
        return render_template('index.html')

    def _add_entry(self) -> str:
        return render_template('index.html')

    def _submit_entry(self) -> str:
        return render_template('index.html')
