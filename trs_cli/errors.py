import logging
import traceback as tb
from types import TracebackType

logger = logging.getLogger(__name__)


def exception_handler(
    _type: type,
    value: BaseException,
    traceback: TracebackType,
    print_traceback: bool = False,
) -> None:
    """Error handler for all exceptions."""
    if print_traceback:
        tb.print_exception(etype=_type, value=value, tb=traceback)
    else:
        msg = ""
        if hasattr(_type, "__name__"):
            msg = (
                f"{_type.__name__}: {value}"
                if str(value)
                else f"{_type.__name__}"
            )
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
