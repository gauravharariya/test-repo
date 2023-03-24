import pytest

from app import create_app, db


@pytest.fixture(scope="session", autouse=True)
def app():
    """
    Create a Flask app context for the tests.
    """
    config = {
        "DEBUG": True,
        "TESTING": True,
        "APP_NAME": "test-app",
        "ENABLE_OPENAPI_SPEC": False,
        "API_TITLE": "Test API",
        "API_VERSION": 1,
        "OPENAPI_VERSION": "3.0.2",
        # cognito
        "COGNITO_REGION": "test-region",
        "COGNITO_USERPOOL_ID": "test-userpool-id",
        "COGNITO_JWT_HEADER_NAME": "Authorization",
        "COGNITO_ISSUER": "test-issuer",
        "COGNITO_TOKEN_URL": "https://example.com/oauth/token",
        # orm
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    }
    _app = create_app(config)
    with _app.app_context():
        yield _app


@pytest.fixture(scope="session")
def db_session(app):
    """
    Provide the transactional fixtures with access to the database via a Flask-SQLAlchemy
    database connection.
    """
    # create schemas necessary for app
    # attach configuration and metadata as databases
    db.session.execute("ATTACH ':memory:' AS configuration")
    db.session.execute("ATTACH ':memory:' AS metadata")
    db.session.commit()
    db.create_all()
    yield db.session
    db.drop_all()
