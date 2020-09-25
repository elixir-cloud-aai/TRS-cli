"""Unit tests for TRS client."""

# TODO: implement
# Check TRS-cli repo for examples

import pytest
import unittest

from trs_cli.client import TRSClient
from trs_cli.errors import (
    InvalidURI,
    InvalidResourcedentifier
)
import requests_mock
import requests

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
MOCK_PORT = 443
MOCK_BASE_PATH = "a/b/c"
MOCK_ID = "123456"
MOCK_TOKEN = "MyT0k3n"
MOCK_TRS_URL = f"{MOCK_HOST}:{MOCK_PORT}/a/b/c/tools"

MOCK_TOOL_CLASS = {
    "description": "description",
    "id": MOCK_ID,
    "name": "name",
}

MOCK_FILES = {
    "file_wrapper": {
        "checksum": [
            {
                "checksum": "checksum",
                "type": "sha1",
            }
        ],
        "content": "content",
        "url": "url",
    },
    "tool_file": {
        "file_type": "PRIMARY_DESCRIPTOR",
        "path": "path",
    },
    "type": "CWL"
}

MOCK_IMAGES = [
    {
        "checksum": [
            {
                "checksum": "checksums",
                "type": "sha256"
            }
        ],
        "image_name": "image_name",
        "image_type": "Docker",
        "registry_host": "registry_host",
        "size": 0,
        "updated": "updated",
    }
]

MOCK_VERSION_NO_ID = {
    "author": [
        "author"
    ],
    "descriptor_type": [
        "CWL"
    ],
    "files": MOCK_FILES,
    "images": MOCK_IMAGES,
    "included_apps": [
        "https://bio.tools/tool/mytum.de/SNAP2/1",
        "https://bio.tools/bioexcel_seqqc"
    ],
    "is_production": True,
    "name": "name",
    "signed": True,
    "verified_source": [
        "verified_source",
    ]
}

MOCK_TOOL = {
    "aliases": [
        "alias_1",
        "alias_2",
        "alias_3",
    ],
    "checker_url": "checker_url",
    "description": "description",
    "has_checker": True,
    "name": "name",
    "organization": "organization",
    "toolclass": MOCK_TOOL_CLASS,
    "versions": [
        MOCK_VERSION_NO_ID,
    ],
}

MOCK_ERROR = {
    "msg": "mock_message",
    "status_code": "400"
}

MOCK_VERSION_ID = "version"

MOCK_TOOL_ID_AND_VERSION_URL = f"{MOCK_HOST}:{MOCK_PORT}/a/b/c/tools/" \
    f"{MOCK_ID}/versions/{MOCK_VERSION_ID}"

MOCK_TOOL_ID = f"{MOCK_HOST}:{MOCK_PORT}/a/b/c/tools/{MOCK_ID}"

MOCK_ID_URL = f"trs://fakehost.com/{MOCK_ID}"

MOCK_VERSION_ID_URL = f"trs://fakehost.com/{MOCK_ID}" \
    f"/versions/{MOCK_VERSION_ID}"


class TestTRSClient(unittest.TestCase):

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        base_path=MOCK_BASE_PATH,
    )

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

    def test_get_tool_version(self):
        """Test get_tool_version url"""
        with requests_mock.Mocker() as m:
            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}",
                status_code=200,
                json=MOCK_TOOL,
            )
            self.cli._get_tool_version(tool_id=MOCK_ID)
            self.assertEqual(
                m.last_request.url,
                f"{MOCK_TRS_URL}/{MOCK_ID}",
            )

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}",
                status_code=200,
                json=MOCK_TOOL,
            )
            self.cli._get_tool_version(tool_id=MOCK_ID)
            self.assertEqual(
                m.last_request.url,
                f"{MOCK_TRS_URL}/{MOCK_ID}",
            )

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}",
                status_code=200,
                json=MOCK_TOOL,
            )
            self.cli._get_tool_version(tool_id=MOCK_ID_URL)
            self.assertEqual(
                m.last_request.url,
                f"{MOCK_TRS_URL}/{MOCK_ID}",
            )

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}/versions/{MOCK_VERSION_ID}",
                status_code=200,
                json=MOCK_TOOL,
            )
            self.cli._get_tool_version(tool_id=MOCK_VERSION_ID_URL)
            self.assertEqual(
                m.last_request.url,
                f"{MOCK_TRS_URL}/{MOCK_ID}/versions/{MOCK_VERSION_ID}",
            )

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}/versions/{MOCK_VERSION_ID}",
                status_code=200,
                json=MOCK_TOOL,
            )
            self.cli._get_tool_version(
                tool_id=MOCK_ID, version_id=MOCK_VERSION_ID)
            self.assertEqual(
                m.last_request.url,
                f"{MOCK_TRS_URL}/{MOCK_ID}/versions/{MOCK_VERSION_ID}",
            )

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}",
                exc=requests.exceptions.ConnectionError
            )
            with pytest.raises(requests.exceptions.ConnectionError):
                self.cli._get_tool_version(tool_id=MOCK_ID)

            m.get(
                f"{self.cli.uri}/tools/{MOCK_ID}/versions/{MOCK_VERSION_ID}",
                status_code=404,
                text="mock_text",
            )

            with pytest.raises(InvalidResourcedentifier):
                self.cli._get_tool_version(
                    tool_id=MOCK_ID, version_id=MOCK_VERSION_ID)
