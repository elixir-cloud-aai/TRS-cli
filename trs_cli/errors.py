import logging
from types import TracebackType

logger = logging.getLogger(__name__)


def exception_handler(
    _type: type,
    value: BaseException,
    traceback: TracebackType
) -> None:
    """Error handler for all exceptions."""
    if str(value):
        msg = f"{_type.__name__}: {value}"
    else:
        msg = f"{_type.__name__}"
    logger.error(msg)


class InvalidURI(Exception):
    """Exception raised for invalid URIs."""


class InvalidResourcedentifier(Exception):
    """Exception raised when an invalid API response is encountered."""
