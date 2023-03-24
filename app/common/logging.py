import logging

from flask import has_request_context, request


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


custom_formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
    "%(levelname)s in %(module)s: %(message)s"
)


# default_handler.setFormatter(formatter)


def get_logger(name=None, level="DEBUG"):
    _logger = logging.getLogger(name or __file__)
    # this fixes the duplicated logs in Lambda
    _logger.handlers = []
    # this stops propagating any message to Lambda's default logger
    _logger.propagate = False

    log_level = logging.getLevelName(level)
    _logger.setLevel(log_level)
    channel = logging.StreamHandler()
    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # )
    channel.setFormatter(custom_formatter)
    _logger.addHandler(channel)
    return _logger


logger = get_logger(level="INFO")
