"""Unit tests for TRS client."""

# TODO: implement
# Check TRS-cli repo for examples

import pytest
import unittest

from trs_cli.client import TRSClient
from trs_cli.errors import (
    InvalidURI
)

MOCK_HOST = "https://fakehost.com"
MOCK_TRS_URI = "trs://fakehost.com/SOME_OBJECT"
MOCK_TRS_URI_LONG = (
    "trs://aaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaaa"
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaa.com/SOME_OBJECT"
)
MOCK_TRS_URI_INVALID = "tr://fakehost.com/SOME_OBJECT"
MOCK_PORT = 8080
MOCK_BASE_PATH = "a/b/c"
MOCK_TOKEN = "MyT0k3n"
MOCK_TRS_URL = f"{MOCK_HOST}:{MOCK_PORT}/ga4gh/drs/v1/objects"


class TestTRSClient(unittest.TestCase):

    def test_cli(self):
        """Test url attribute"""
        cli = TRSClient(
            uri=MOCK_HOST,
            port=MOCK_PORT,
            base_path=MOCK_BASE_PATH,
        )
        self.assertEqual(
            cli.uri,
            f"{MOCK_HOST}:{MOCK_PORT}/{MOCK_BASE_PATH}",
        )
        cli = TRSClient(
            uri=MOCK_TRS_URI,
            base_path=MOCK_BASE_PATH,
            token=MOCK_TOKEN,
        )
        self.assertEqual(
            cli.uri,
            f"{MOCK_HOST}:443/{MOCK_BASE_PATH}"
        )

        with pytest.raises(InvalidURI):
            cli = TRSClient(
                uri=MOCK_TRS_URI_INVALID,
                base_path=MOCK_BASE_PATH,
            )

        with pytest.raises(InvalidURI):
            cli = TRSClient(
                uri=MOCK_TRS_URI_LONG,
                base_path=MOCK_BASE_PATH,
            )
