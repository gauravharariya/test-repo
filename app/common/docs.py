def build_spec_security(app, spec):
    """
    Generate security scheme for spec
    """
    # If no auth URL found, then don't need to add ouath2 auth scheme
    # e.g. In local we might not need auth scheme
    oidc_auth_url = app.config.get("COGNITO_TOKEN_URL")
    if oidc_auth_url is None:
        return

    security = [
        {"AuthServer": []},
    ]
    spec.options.update(security=security)
    spec.components.security_scheme(
        "AuthServer",
        {
            "description": "Authentication via Cognito(OAuth2)",
            "type": "oauth2",
            "flows": {
                "clientCredentials": {"tokenUrl": app.config["COGNITO_TOKEN_URL"]}
            },
        },
    )
