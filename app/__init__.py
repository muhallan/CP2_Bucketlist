from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    """
    Method used to create an app and initialize it with the required configurations
    :param config_name:
    :return: app
    """
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config.from_object(app_config[config_name])

    # for removing trailing slashes enforcement
    app.url_map.strict_slashes = False
    db.init_app(app)

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # import the bucketlists blueprint and register it on the app
    from .bucketlists import bucketlists_blueprint
    app.register_blueprint(bucketlists_blueprint)

    return app
