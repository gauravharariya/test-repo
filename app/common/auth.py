from collections import OrderedDict
from functools import wraps

from cognitojwt import CognitoJWTException, decode as cognito_jwt_decode
from flask import current_app, jsonify, request, g
from jose.exceptions import JWTError
from werkzeug.local import LocalProxy

from app.common.logging import get_logger

LOGGER = get_logger(__name__)

CONFIG_DEFAULTS = {
    "COGNITO_CHECK_TOKEN_EXPIRATION": True,
    "COGNITO_JWT_HEADER_NAME": "Authorization",
    "COGNITO_JWT_HEADER_PREFIX": "Bearer",
}

# user from pool
current_user = LocalProxy(lambda: getattr(g, "user", None))

# access initialized cognito extension
_cog = LocalProxy(lambda: current_app.extensions["cognito_auth"])


# User models which holds the logged-in service user and scopes
class ServiceUser:
    def __init__(self, client_id, scopes):
        self.client_id = client_id
        self.scopes = scopes

    def __str__(self):
        return f"ServiceUser({self.client_id})"

    def __repr__(self):
        return f"ServiceUser({self.client_id})"


class CognitoAuthError(Exception):
    def __init__(self, error, description, status_code=401, headers=None):
        self.error = error
        self.description = description
        self.status_code = status_code
        self.headers = headers

    def __repr__(self):
        return f"CognitoAuthError: {self.error}"

    def __str__(self):
        return f"{self.error} - {self.description}"


class CognitoAuth:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        for key, value in CONFIG_DEFAULTS.items():
            app.config.setdefault(key, value)

        # required configuration
        self.app_name = self._get_required_config(app, "APP_NAME")
        self.region = self._get_required_config(app, "COGNITO_REGION")
        self.userpool_id = self._get_required_config(app, "COGNITO_USERPOOL_ID")
        self.jwt_header_name = self._get_required_config(app, "COGNITO_JWT_HEADER_NAME")
        self.jwt_header_prefix = self._get_required_config(
            app, "COGNITO_JWT_HEADER_PREFIX"
        )

        # save for localproxy
        app.extensions["cognito_auth"] = self

        # handle CognitoJWTExceptions
        app.errorhandler(CognitoAuthError)(self._cognito_auth_error_handler)

    def _get_required_config(self, app, config_name):
        val = app.config.get(config_name)
        if not val:
            raise Exception(
                f"{config_name} not found in app configuration but it is required."
            )
        return val

    @staticmethod
    def get_token():
        """Get token from request."""
        auth_header_name = _cog.jwt_header_name
        auth_header_prefix = _cog.jwt_header_prefix

        # get token value from header
        auth_header_value = request.headers.get(auth_header_name)

        if not auth_header_value:
            # no auth header found
            return None

        parts = auth_header_value.split()

        if not auth_header_prefix:
            if len(parts) > 1:
                raise CognitoAuthError(
                    "Invalid Cognito JWT Header", "Token contains spaces"
                )
            return auth_header_value

        if parts[0].lower() != auth_header_prefix.lower():
            raise CognitoAuthError(
                "Invalid Cognito JWT header",
                "Unsupported authorization type. Header prefix does not match.",
            )
        if len(parts) == 1:
            raise CognitoAuthError("Invalid Cognito JWT header", "Token missing")
        if len(parts) > 2:
            raise CognitoAuthError(
                "Invalid Cognito JWT header", "Token contains spaces"
            )

        return parts[1]

    def get_user(self, jwt_payload):
        """Get application service/user identity from Cognito JWT payload."""
        client_id = jwt_payload.get("client_id")
        scopes = self._get_app_scopes(jwt_payload)
        return ServiceUser(client_id, scopes)

    def _get_app_scopes(self, jwt_payload):
        scope_str = jwt_payload.get("scope")
        scopes = scope_str.split(" ")
        app_scopes = [
            scope.replace(f"{self.app_name}/", "")
            for scope in scopes
            if self.app_name in scope
        ]
        return app_scopes

    def _cognito_auth_error_handler(self, error):
        LOGGER.error("Authentication Failure", exc_info=error)
        return (
            jsonify(
                OrderedDict(
                    [
                        ("error", error.error),
                        ("description", error.description),
                    ]
                )
            ),
            error.status_code,
            error.headers,
        )

    def decode_token(self, token):
        """Decode token."""
        try:
            return cognito_jwt_decode(
                token=token, region=self.region, userpool_id=self.userpool_id
            )
        except (ValueError, JWTError) as exc:
            raise CognitoJWTException("Malformed Authentication Token") from exc


def auth_required(func):
    """View decorator that requires a valid Cognito JWT token
    to be present in the request."""

    @wraps(func)
    def decorator(*args, **kwargs):
        _auth_required()
        return func(*args, **kwargs)

    return decorator


def check_scopes(scopes: list):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            _check_scopes(scopes)
            return function(*args, **kwargs)

        return wrapper

    return decorator


def _check_scopes(scopes: list):
    """
    Does the actual work of verifying the user copes
    to restrict access to some resources.
    :param scopes a list with the name of the scopes of Cognito Identity Pool
    :raise an exception if there is no scope
    """

    if current_user is None:
        raise CognitoAuthError(
            "Not Authorized",
            "User doesn't have access to this resource",
            status_code=403,
        )

    if "*" not in current_user.scopes and all(  # noqa
        [scope not in current_user.scopes for scope in scopes]
    ):
        raise CognitoAuthError(
            "Not Authorized",
            "User doesn't have access to this resource",
            status_code=403,
        )


def _auth_required():
    """Does the actual work of verifying the Cognito JWT data in the request."""
    token = _cog.get_token()

    if token is None:
        auth_header_name = _cog.jwt_header_name
        raise CognitoAuthError(
            "Authorization Required",
            f'Request does not contain a access token in the "{auth_header_name}" header.',  # noqa
        )

    try:
        # check if token is signed by user pool
        payload = _cog.decode_token(token=token)
    except CognitoJWTException as exc:
        LOGGER.error("Authentication Failure", exc_info=exc)
        raise CognitoAuthError(
            "Invalid Cognito Authentication Token", str(exc)
        ) from exc

    g.cognito_jwt = payload
    g.user = _cog.get_user(payload)
