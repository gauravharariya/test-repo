import os
from os import environ

from dotenv import load_dotenv
from snowflake.sqlalchemy import URL  # noqa

from app.common.utils import load_private_key

# useful in local, for others env will come from ECS
load_dotenv(".env")  # take environment variables from .env.

DEBUG = environ.get("DEBUG", False)  # Turns on debugging features in Flask

# name of the app added into scopes
APP_NAME = environ.get("APP_NAME", "galactic_core")

# Open API spec
API_TITLE = "Galactic Core API"
API_VERSION = environ.get("API_VERSION", 1)
OPENAPI_VERSION = "3.0.2"
ENABLE_OPENAPI_SPEC = environ.get("ENABLE_OPENAPI_SPEC", True)
OPENAPI_JSON_PATH = "openapi.json" if environ.get("ENABLE_SWAGGER", True) else None
OPENAPI_URL_PREFIX = "/"
OPENAPI_SWAGGER_UI_PATH = "/docs/"
OPENAPI_SWAGGER_UI_URL = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/4.15.5/"
OPENAPI_SWAGGER_UI_CONFIG = {
    "defaultModelsExpandDepth": 3,
    "defaultModelExpandDepth": 3,
    "defaultModelRendering": "example",
    "showCommonExtensions": True,
    "showExtensions": True,
    "docExpansion": "list",
    "requestSnippetsEnabled": True,
}

# Snowflake setup
db_params = dict(
    user=environ["SNOWFLAKE_USER"],
    account=environ["SNOWFLAKE_ACCOUNT"],
    database=environ["SNOWFLAKE_DATABASE"],
    warehouse=environ["SNOWFLAKE_WAREHOUSE"],
    schema=environ["SNOWFLAKE_SCHEMA"],
)
if environ.get("SNOWFLAKE_REGION"):
    db_params["region"] = environ.get("SNOWFLAKE_REGION")
if environ.get("SNOWFLAKE_ROLE"):
    db_params["role"] = environ.get("SNOWFLAKE_ROLE")

SQLALCHEMY_DATABASE_URI = URL(**db_params)
SQLALCHEMY_ECHO = True  # https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
# private key
if environ.get("SNOWFLAKE_PRIVATE_KEY"):
    SNOWFLAKE_PRIVATE_KEY = environ["SNOWFLAKE_PRIVATE_KEY"].encode("utf-8")
else:
    SNOWFLAKE_PRIVATE_KEY = open("rsa_key.p8", "rb").read()  # noqa
SQLALCHEMY_ENGINE_OPTIONS = {
    "connect_args": {
        "client_session_keep_alive": True,
        "private_key": load_private_key(
            SNOWFLAKE_PRIVATE_KEY, environ["SNOWFLAKE_PRIVATE_KEY_PASSWORD"]
        ),
    }
}
JSON_SORT_KEYS = False

# Cognito
COGNITO_USERPOOL_ID = environ["COGNITO_USERPOOL_ID"]
COGNITO_REGION = environ["COGNITO_REGION"]
COGNITO_ISSUER = environ["COGNITO_ISSUER"]
COGNITO_TOKEN_URL = (
    os.path.join(COGNITO_ISSUER, "oauth2/token") if COGNITO_ISSUER else None
)
