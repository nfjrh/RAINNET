from flask import Flask

from config import Config


def create_app(config_object=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_object)

    from . import db
    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
