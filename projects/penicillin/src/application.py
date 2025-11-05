from typing import Optional

import flask_injector
from flask import Flask
from materiatechnica.penicillin.config import Config, TestConfig
from materiatechnica.penicillin.module import PenicillinModule
from materiatechnica.penicillin.monitoring import setup_monitoring
from materiatechnica.penicillin.routes import healthchecks, runs


def create_app(config: Optional[Config]) -> Flask:
    flask_app = Flask(__name__)
    if not config:
        config = Config()
    flask_app.config.from_object(config)
    flask_app.register_blueprint(runs.runs)
    flask_app.register_blueprint(healthchecks.health)
    if config.ENABLE_MONITORING:
        setup_monitoring(flask_app)
    flask_injector.FlaskInjector(app=flask_app, modules=[PenicillinModule()])
    return flask_app


if __name__ == "__main__":
    create_app(config=TestConfig()).run(port=5001, host="127.0.0.1", debug=True)
