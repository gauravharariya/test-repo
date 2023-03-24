from unittest.mock import MagicMock

from app import build_spec_security


def test_build_spec_security_no_auth_url():
    app = MagicMock(config={})
    spec = MagicMock(options={})

    build_spec_security(app, spec)

    assert "security" not in spec.options


def test_build_spec_security_with_auth_url():
    app = MagicMock(config={"COGNITO_TOKEN_URL": "https://example.com/token"})
    spec = MagicMock(options={}, components=MagicMock())

    build_spec_security(app, spec)

    assert "security" in spec.options

    spec.components.security_scheme.assert_called_once_with(
        "AuthServer",
        {
            "description": "Authentication via Cognito(OAuth2)",
            "type": "oauth2",
            "flows": {"clientCredentials": {"tokenUrl": "https://example.com/token"}},
        },
    )
