"""Unit tests for errors/handlers."""

import sys

from trs_cli.errors import exception_handler


ERROR_MSG = "SYSTEM HANDLER"
ERROR_MSG_CUSTOM_HANDLER = "CUSTOM HANDLER"


class TestExceptionHandler:

    def test_none_type(self):
        ret_val = exception_handler(*sys.exc_info())
        assert ret_val is None

    def test_exc(self):
        try:
            raise Exception(ERROR_MSG)
        except Exception as exc:
            exception_handler(*sys.exc_info())
            assert str(exc) == ERROR_MSG

    def test_exc_with_tb(self):
        try:
            raise Exception(ERROR_MSG)
        except Exception as exc:
            exception_handler(*sys.exc_info(), print_traceback=True)
            assert str(exc) == ERROR_MSG
