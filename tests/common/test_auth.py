from copy import deepcopy
from unittest.mock import Mock, MagicMock

import pytest
from cognitojwt import CognitoJWTException

from app.common import auth
from app.common.auth import ServiceUser, CognitoAuth, auth_required, CognitoAuthError


class objectview(object):  # noqa
    def __init__(self, d):
        self.__dict__ = d


@pytest.fixture
def cog(app):
    ca = CognitoAuth(app)
    app.extensions["cognito_auth"] = ca
    return ca


@pytest.fixture
def current_user():
    return ServiceUser(client_id="test", scopes=["admin"])


def test_cognito_auth_init(app):

    cognito_auth = CognitoAuth(app)

    assert cognito_auth.app_name == "test-app"
    assert cognito_auth.region == "test-region"
    assert cognito_auth.userpool_id == "test-userpool-id"
    assert cognito_auth.jwt_header_name == "Authorization"
    assert cognito_auth.jwt_header_prefix == "Bearer"

    assert app.extensions["cognito_auth"] == cognito_auth


def test_service_user():
    # Create a ServiceUser object
    user = ServiceUser("12345", ["foo", "bar"])

    # Check that the client ID and scopes are set correctly
    assert user.client_id == "12345"
    assert user.scopes == ["foo", "bar"]


def test_get_user(cog):
    # Define a JWT payload with the client ID and scope
    jwt_payload = {
        "client_id": "12345",
        "scope": "test-app/foo test-app/bar otherapp/baz",
    }

    # Call the get_user() method and check the result
    user = cog.get_user(jwt_payload)
    assert user.client_id == "12345"
    assert user.scopes == ["foo", "bar"]


def test_decode_token(cog, monkeypatch):

    # Define a test JWT token
    sample = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"  # noqa

    # Mock the cognito_jwt_decode function
    mock_decode = MagicMock()
    mock_decode.return_value = {"sub": "1234", "name": "John Doe", "iat": 1617068205}
    monkeypatch.setattr("app.common.auth.cognito_jwt_decode", mock_decode)

    # Call the decode_token method with the test token
    decoded_token = cog.decode_token(sample)

    # Check that the decoded token contains the expected fields
    assert "sub" in decoded_token
    assert "name" in decoded_token
    assert "iat" in decoded_token

    # Test handling of malformed tokens
    mock_decode.side_effect = ValueError("Malformed token")
    with pytest.raises(CognitoJWTException):
        cog.decode_token(sample)


def test_valid_header_prefix():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": "Bearer"}
    )
    get_mock = Mock(return_value="Bearer Test")
    request_mock = objectview({"headers": objectview({"get": get_mock})})

    auth.request = request_mock

    ca = auth.CognitoAuth()
    result = ca.get_token()
    assert result == "Test"


def test_incorrect_header_prefix():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": "Bearer"}
    )

    get_mock = Mock(return_value="Something Test")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    with pytest.raises(auth.CognitoAuthError):
        ca.get_token()


def test_malformed_header():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": "Bearer"}
    )

    get_mock = Mock(return_value="Something To Fail")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    with pytest.raises(auth.CognitoAuthError):
        ca.get_token()


def test_malformed_header2():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": "Bearer"}
    )

    get_mock = Mock(return_value="Fail")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    with pytest.raises(auth.CognitoAuthError):
        ca.get_token()


def test_with_prefix_empty_string():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": ""}
    )

    get_mock = Mock(return_value="Something")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    result = ca.get_token()
    assert "Something" == result


def test_with_prefix_none():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": None}
    )

    get_mock = Mock(return_value="Something")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    result = ca.get_token()
    assert "Something" == result


def test_without_prefix_malformed():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": None}
    )

    get_mock = Mock(return_value="Something Else")
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    with pytest.raises(auth.CognitoAuthError):
        ca.get_token()


def test_without_prefix_missing():
    auth._cog = objectview(
        {"jwt_header_name": "Authorization", "jwt_header_prefix": None}
    )

    get_mock = Mock(return_value=None)
    request_mock = objectview({"headers": objectview({"get": get_mock})})
    auth.request = request_mock
    ca = auth.CognitoAuth()
    result = ca.get_token()
    assert result is None


def test_scopes_decorator(current_user):
    auth.current_user = current_user

    @auth.check_scopes(["admin"])
    def some_func():
        return True

    assert some_func()


def test_scopes_fail_if_no_user():
    auth.current_user = None

    @auth.check_scopes(["other"])
    def some_func():
        return True

    with pytest.raises(auth.CognitoAuthError):
        some_func()


def test_scopes_fail_if_not_in_scopes(current_user):
    auth.current_user = current_user

    @auth.check_scopes(["other"])
    def some_func():
        return True

    with pytest.raises(auth.CognitoAuthError):
        some_func()


def test_scopes_fail_if_no_scopes(current_user):
    auth.current_user = deepcopy(current_user)
    auth.current_user.scopes = []

    @auth.check_scopes(["admin"])
    def some_func():
        return True

    with pytest.raises(auth.CognitoAuthError):
        some_func()


def test_auth_required_happy_path(cog, app, monkeypatch):
    with app.test_request_context():
        auth._cog = cog
        # set up the mock for get_token method
        mock_get_token = MagicMock(return_value="valid")
        monkeypatch.setattr(auth._cog, "get_token", mock_get_token)

        # set up the mock for decode_token method
        mock_decode_token = MagicMock(
            return_value={
                "client_id": "12345",
                "scope": "test-app/foo test-app/bar otherapp/baz",
            }
        )
        monkeypatch.setattr(auth._cog, "decode_token", mock_decode_token)

        # define a view function to decorate
        @auth_required
        def view_function():
            return "OK"

        # call the view function
        response = view_function()

        # check that the response is "OK"
        assert response == "OK"

        # check that get_token method was called once
        mock_get_token.assert_called_once()

        # check that decode_token method was called once with "valid_token" argument
        mock_decode_token.assert_called_once_with(token="valid")  # nosec


def test_auth_required_missing_token(cog, app, monkeypatch):
    with app.test_request_context():
        auth._cog = cog
        # set up the mock for get_token method
        mock_get_token = MagicMock(return_value=None)
        monkeypatch.setattr(auth._cog, "get_token", mock_get_token)

        # define a view function to decorate
        @auth_required
        def view_function():
            return "OK"

        # call the view function and catch the exception
        with pytest.raises(CognitoAuthError):
            view_function()

        # check that get_token method was called once
        mock_get_token.assert_called_once()


def test_auth_required_malformed_token(cog, app, monkeypatch):
    with app.test_request_context():
        auth._cog = cog
        # set up the mock for get_token method
        mock_get_token = MagicMock(return_value="invalid")
        monkeypatch.setattr(auth._cog, "get_token", mock_get_token)

        # set up the mock for decode_token method
        mock_decode_token = MagicMock(
            side_effect=CognitoJWTException("Malformed Authentication Token")
        )
        monkeypatch.setattr(auth._cog, "decode_token", mock_decode_token)

        # define a view function to decorate
        @auth_required
        def view_function():
            return "OK"

        # call the view function and catch the exception
        with pytest.raises(CognitoAuthError):
            view_function()

        # check that get_token method was called once
        mock_get_token.assert_called_once()

        # check that decode_token method was called once with "invalid_token" argument
        mock_decode_token.assert_called_once_with(token="invalid")  # nosec
