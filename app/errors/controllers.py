from flask import make_response, jsonify

from flask_smorest import Blueprint
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(403)
@errors.app_errorhandler(404)
def api_error_handler(exc: HTTPException):
    return make_response(jsonify(code=exc.code, error=exc.description), exc.code)


@errors.app_errorhandler(400)
def api_validation_error_handler(exc: HTTPException):
    validation_err = exc.description

    if validation_err is not None and isinstance(validation_err, ValidationError):
        return make_response(
            jsonify(
                code=exc.code,
                error="Validation Error",
                error_details=validation_err.messages,
            ),
            exc.code,
        )

    return make_response(jsonify(code=exc.code, error=exc.description))
