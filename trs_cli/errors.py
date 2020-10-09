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


class ContentTypeUnavailable(Exception):
    """Exception raised when an unavailable content type is requested."""


class FileInformationUnavailable(Exception):
    """Exception raised when information for a file associated with a
    descriptor is unavailable.
    """


class InvalidURI(Exception):
    """Exception raised for invalid URIs."""


class InvalidResourceIdentifier(Exception):
    """Exception raised for invalid tool/version identifiers."""


class InvalidResponseError(Exception):
    """Exception raised when an invalid API response is encountered."""


class InvalidPayload(Exception):
    """Exception raised when an invalid payload is encountered."""
