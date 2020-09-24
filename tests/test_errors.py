"""Unit tests for errors/handlers."""

import sys

import pytest

from trs_cli.errors import exception_handler


ERROR_MSG = "SYSTEM HANDLER"
ERROR_MSG_CUSTOM_HANDLER = "CUSTOM HANDLER"


def test_exception_handler():
    sys.excepthook = sys.__excepthook__
    with pytest.raises(Exception) as e:
        raise Exception(ERROR_MSG)
        assert str(e.value) == ERROR_MSG

    test_handler = exception_handler(
        _type=Exception,
        value=Exception(ERROR_MSG_CUSTOM_HANDLER),
        traceback=sys.exc_info()[2],
    )
    sys.excepthook = test_handler
    with pytest.raises(Exception) as e:
        raise Exception(ERROR_MSG)
        assert str(e.value) == ERROR_MSG_CUSTOM_HANDLER

    test_handler_no_msg = exception_handler(
        _type=Exception,
        value=Exception(),
        traceback=sys.exc_info()[2],
    )
    sys.excepthook = test_handler_no_msg
    with pytest.raises(Exception) as e:
        raise Exception(ERROR_MSG_CUSTOM_HANDLER)
        assert str(e.value) is None

    sys.excepthook = sys.__excepthook__
