from flask import Flask
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from app.common.auth import CognitoAuth
from app.common.docs import build_spec_security

s_api = Api()

db = SQLAlchemy()
migrate = Migrate()
auth = CognitoAuth()


def create_app(test_config=None):
    """Application-factory pattern"""
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py")
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # initialize extension instances

    # initialize db
    from app import models  # pylint: disable=cyclic-import # noqa

    db.init_app(app)
    migrate.init_app(app, db)

    # initiate the api
    s_api.init_app(app)
    # add security spec
    build_spec_security(app, s_api.spec)

    # initialize cognito auth
    auth.init_app(app)

    # version v1
    from app.v1 import blp as blp_v1  # pylint: disable=cyclic-import # noqa

    s_api.register_blueprint(blp_v1, url_prefix="/v1")

    # register error blueprint
    from app.errors import errors as blp_errors  # noqa

    s_api.register_blueprint(blp_errors)

    return app
