"""Unit tests for TRS client."""

from copy import deepcopy
import pathlib  # noqa: F401

from pydantic import ValidationError
import pytest
import requests
import responses
from unittest.mock import mock_open, patch

from trs_cli.client import TRSClient
from trs_cli.errors import (
    ContentTypeUnavailable,
    FileInformationUnavailable,
    InvalidResponseError,
    InvalidResourceIdentifier,
    InvalidURI,
)
from trs_cli.models import (
    Error,
    Tool,
    DescriptorType,
    ImageType,
    )

MOCK_DOMAIN = "x.y.z"
MOCK_HOST = f"https://{MOCK_DOMAIN}"
MOCK_PORT = 4434
MOCK_BASE_PATH = "a/b/c"
MOCK_API = f"{MOCK_HOST}:{MOCK_PORT}/{MOCK_BASE_PATH}"
MOCK_ID = "123456"
MOCK_ID_INVALID = "N0T VAL!D"
MOCK_TRS_URI = f"trs://{MOCK_DOMAIN}/{MOCK_ID}"
MOCK_TRS_URI_VERSIONED = f"trs://{MOCK_DOMAIN}/{MOCK_ID}/versions/{MOCK_ID}"
MOCK_TOKEN = "MyT0k3n"
MOCK_DESCRIPTOR = "CWL"
MOCK_RESPONSE_INVALID = {"not": "valid"}
MOCK_DIR = "/mock/directory"
MOCK_SERVICE_INFO = {
  "id": "TEMPID1",
  "name": "TEMP_STUB",
  "type": {
    "group": "TEMP_GROUP",
    "artifact": "TEMP_ARTIFACT",
    "version": "v1"
  },
  "organization": {
    "name": "Parent organization",
    "url": "https://parent.abc"
  },
  "version": "0.0.0"
}
MOCK_ERROR = {
    "code": 400,
    "message": "BadRequest",
}
MOCK_FILE_WRAPPER = {
    "checksum": [
        {
            "checksum": "checksum",
            "type": "sha1",
        }
    ],
    "content": "content",
    "url": "url",
}
MOCK_TOOL_FILE = {
    "file_type": "PRIMARY_DESCRIPTOR",
    "path": MOCK_ID,
}
MOCK_VERSION = {
    "author": [
        "author"
    ],
    'containerfile': None,
    'descriptor_type': [DescriptorType.CWL],
    "id": "v1",
    "images": [
          {
            "checksum": [
              {
                "checksum": "77af4d6b9913e693e8d0b4b294fa62ade \
                    6054e6b2f1ffb617ac955dd63fb0182",
                "type": "sha256"
              }
            ],
            "image_name": "string",
            "image_type": ImageType.Docker,
            "registry_host": "string",
            "size": 0,
            "updated": "string"
          }
        ],
    "included_apps": [
        "https://bio.tools/tool/mytum.de/SNAP2/1",
        "https://bio.tools/bioexcel_seqqc"
    ],
    "is_production": True,
    "meta_version": None,
    "name": "name",
    "signed": True,
    "url": "abcde.com",
    "verified": None,
    "verified_source": [
        "verified_source",
    ]
}
MOCK_VERSION_POST = {
    "author": [
        "author"
    ],
    'descriptor_type': None,
    "images": None,
    "included_apps": [
        "https://bio.tools/tool/mytum.de/SNAP2/1",
        "https://bio.tools/bioexcel_seqqc"
    ],
    "is_production": True,
    "name": "name",
    "signed": True,
    "verified": None,
    "verified_source": [
        "verified_source",
    ]
}
MOCK_TOOL_CLASS_WITH_ID = {
    "description": "description",
    "id": "234561",
    "name": "name",
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
    "id": MOCK_ID,
    "meta_version": "1",
    "name": "name",
    "organization": "organization",
    "toolclass": MOCK_TOOL_CLASS_WITH_ID,
    "url": "abc.com",
    "versions": [
        MOCK_VERSION
    ]
}
MOCK_TOOL_POST = {
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
    "toolclass": MOCK_TOOL_CLASS_WITH_ID,
    "versions": [
        MOCK_VERSION_POST
    ]
}
MOCK_TOOL_CLASS = {
    "description": "string",
    "id": "string",
    "name": "string"
}
MOCK_TOOL_CLASS_POST = {
    "description": "string",
    "name": "string"
}


def _raise(exception) -> None:
    """General purpose exception raiser."""
    raise exception


class TestTRSClientConstructor:
    """Test TRSClient() construction."""

    def test_individiual_parts(self):
        """Provide individiual parts."""
        cli = TRSClient(
            uri=MOCK_HOST,
            port=MOCK_PORT,
            base_path=MOCK_BASE_PATH,
            use_http=True,
            token=MOCK_TOKEN,
        )
        assert cli.uri == MOCK_API

    def test_trs_uri(self):
        """Provide TRS URI."""
        cli = TRSClient(uri=MOCK_TRS_URI)
        assert cli.uri == f"https://{MOCK_DOMAIN}:443/ga4gh/trs/v2"

    def test_trs_uri_http(self):
        """Provide TRS URI, force HTTP."""
        cli = TRSClient(
            uri=MOCK_TRS_URI,
            use_http=True,
        )
        assert cli.uri == f"http://{MOCK_DOMAIN}:80/ga4gh/trs/v2"


class TestPostServiceInfo:
    """Test poster for service info."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/service-info"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.post(self.endpoint)
        r = self.cli.post_service_info(
            payload=MOCK_SERVICE_INFO
        )
        assert r is None

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.post_service_info(
                payload=MOCK_RESPONSE_INVALID
            )


class TestGetServiceInfo:
    """Test getter for service with a given id."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/service-info"

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=MOCK_SERVICE_INFO)
        r = self.cli.get_service_info()
        assert r.dict()['id'] == MOCK_SERVICE_INFO['id']


class TestPostToolClass:
    """Test poster for tool classes."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/toolClasses"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.post(self.endpoint, json=MOCK_ID)
        r = self.cli.post_tool_class(
            payload=MOCK_TOOL_CLASS_POST
        )
        assert r == MOCK_ID

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.post_tool_class(
                payload=MOCK_RESPONSE_INVALID
            )


class TestPutToolClass:
    """Test putter for tool classes."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/toolClasses/{MOCK_ID}"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.put(self.endpoint, json=MOCK_ID)
        r = self.cli.put_tool_class(
            id=MOCK_ID,
            payload=MOCK_TOOL_CLASS_POST
        )
        assert r == MOCK_ID

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.put_tool_class(
                id=MOCK_ID,
                payload=MOCK_RESPONSE_INVALID
            )


class TestDeleteToolClass:
    """Test delete for tool classes."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/toolClasses/{MOCK_ID}"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.delete(self.endpoint, json=MOCK_ID)
        r = self.cli.delete_tool_class(
            id=MOCK_ID,
        )
        assert r == MOCK_ID


class TestPostTool:
    """Test poster for tools."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.post(self.endpoint, json=MOCK_ID)
        r = self.cli.post_tool(
            payload=MOCK_TOOL_POST
        )
        assert r == MOCK_ID

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.post_tool(
                payload=MOCK_RESPONSE_INVALID
            )


class TestPutTool:
    """Test putter for tools."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.put(self.endpoint, json=MOCK_ID)
        r = self.cli.put_tool(
                id=MOCK_ID,
                payload=MOCK_TOOL_POST
            )
        assert r == MOCK_ID

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.put_tool(
                id=MOCK_ID,
                payload=MOCK_RESPONSE_INVALID
            )


class TestDeleteTool:
    """Test delete for tool."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.delete(self.endpoint, json=MOCK_ID)
        r = self.cli.delete_tool(
            id=MOCK_ID,
        )
        assert r == MOCK_ID


class TestPostVersion:
    """Test poster for tool versions."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}/versions"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.post(self.endpoint, json=MOCK_ID)
        r = self.cli.post_version(
            id=MOCK_ID,
            payload=MOCK_VERSION_POST
        )
        assert r == MOCK_ID

    def test_success_ValidationError(self):
        """Raises validation error when incorrect input is provided"""
        with pytest.raises(ValidationError):
            self.cli.post_version(
                id=MOCK_ID,
                payload=MOCK_RESPONSE_INVALID
            )


class TestDeleteVersion:
    """Test delete for tool version."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}"
    )

    def test_success(self, monkeypatch, requests_mock):
        """Returns 200 response."""
        requests_mock.delete(self.endpoint, json=MOCK_ID)
        r = self.cli.delete_version(
            id=MOCK_ID,
            version_id=MOCK_ID
        )
        assert r == MOCK_ID


class TestGetToolClasses:
    """Test getter for tool classes."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/toolClasses"

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL_CLASS])
        r = self.cli.get_tool_classes()
        assert r == [MOCK_TOOL_CLASS]


class TestGetTools:
    """Test getter for tool with the given filters."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/tools"

    def test_success_without_filters(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL])
        r = self.cli.get_tools()
        assert r == [MOCK_TOOL]

    def test_success_with_filters(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL])
        r = self.cli.get_tools(
            id=MOCK_ID,
            alias="alias_1",
            toolClass="name",
            descriptorType="CWL",
            registry="Docker",
            organization="organization",
            name="string",
            toolname="name",
            description="description",
            author="author",
            checker=True,
            limit=1000,
            offset=1
            )
        assert r == [MOCK_TOOL]


class TestGetTool:
    """Test getter for tool with a given id."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/tools/{MOCK_ID}"

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=MOCK_TOOL)
        r = self.cli.get_tool(
            id=MOCK_ID,
        )
        assert r.dict() == MOCK_TOOL


class TestGetVersions:
    """Test getter for versions of tool with a given id."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/tools/{MOCK_ID}/versions"

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=[MOCK_VERSION])
        r = self.cli.get_versions(
            id=MOCK_ID,
        )
        assert r == [MOCK_VERSION]


class TestGetVersion:
    """Test getter for tool version with given tool_id and version_id."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}"

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=MOCK_VERSION)
        r = self.cli.get_version(
            id=MOCK_ID,
            version_id=MOCK_ID,
        )
        assert r.dict() == MOCK_VERSION


class TestGetDescriptor:
    """Test getter for primary descriptor of a given descriptor type."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}/{MOCK_DESCRIPTOR}"
        "/descriptor"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=MOCK_FILE_WRAPPER)
        r = self.cli.get_descriptor(
            type=MOCK_DESCRIPTOR,
            id=MOCK_ID,
            version_id=MOCK_ID,
        )
        assert r.dict() == MOCK_FILE_WRAPPER


class TestGetDescriptorByPath:
    """Test getter for secondary descriptor, test and other files associated
    with a given descriptor type.
    """

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}/{MOCK_DESCRIPTOR}"
        f"/descriptor/{MOCK_ID}"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=MOCK_FILE_WRAPPER)
        r = self.cli.get_descriptor_by_path(
            type=MOCK_DESCRIPTOR,
            id=MOCK_ID,
            version_id=MOCK_ID,
            path=MOCK_ID,
        )
        assert r.dict() == MOCK_FILE_WRAPPER


class TestGetFiles:
    """Test getter for files of a given descriptor type."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}/{MOCK_DESCRIPTOR}"
        "/files"
    )

    def test_success(self, requests_mock):
        """Returns 200 response."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL_FILE])
        r = self.cli.get_files(
            type=MOCK_DESCRIPTOR,
            id=MOCK_ID,
            version_id=MOCK_ID,
        )
        if not isinstance(r, Error):
            assert r[0].file_type.value == MOCK_TOOL_FILE['file_type']
            assert r[0].path == MOCK_TOOL_FILE['path']

    def test_ContentTypeUnavailable(self, requests_mock):
        """Test unavailable content type."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL_FILE])
        with pytest.raises(ContentTypeUnavailable):
            self.cli.get_files(
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
                format=MOCK_ID,
            )

    def test_success_trs_uri_zip(self, requests_mock):
        """Returns 200 ZIP response with TRS URI."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL_FILE])
        r = self.cli.get_files(
            type=MOCK_DESCRIPTOR,
            id=MOCK_TRS_URI_VERSIONED,
            format='zip',
        )
        if not isinstance(r, Error):
            assert r[0].file_type.value == MOCK_TOOL_FILE['file_type']
            assert r[0].path == MOCK_TOOL_FILE['path']


class TestRetrieveFiles:
    """Test retrieving files of a given descriptor type."""

    cli = TRSClient(
        uri=MOCK_TRS_URI,
        token=MOCK_TOKEN,
    )
    endpoint_files = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}/{MOCK_DESCRIPTOR}"
        "/files"
    )
    endpoint_rel_path = (
        f"{cli.uri}/tools/{MOCK_ID}/versions/{MOCK_ID}/{MOCK_DESCRIPTOR}"
        f"/descriptor/{MOCK_ID}"
    )

    def test_out_dir_cannot_be_created_OSError(self, monkeypatch):
        """Connection error occurs."""
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: _raise(OSError)
        )
        with pytest.raises(OSError):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_TRS_URI,
                token=MOCK_TOKEN,
            )

    def test_cannot_get_files_FileInformationUnavailable(
        self,
        monkeypatch,
        requests_mock,
    ):
        """Call to `GET .../files` endpoint returns error response."""
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: None
        )
        requests_mock.get(
            self.endpoint_files,
            json=MOCK_ERROR,
            status_code=400,
        )
        with pytest.raises(FileInformationUnavailable):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
            )

    def test_path_not_set_FileInformationUnavailable(
        self,
        monkeypatch,
        requests_mock,
    ):
        """Path attribute in returned file information object is unset."""
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: None
        )
        files = [deepcopy(MOCK_TOOL_FILE)]
        del files[0]['path']
        requests_mock.get(
            self.endpoint_files,
            json=files,
        )
        with pytest.raises(FileInformationUnavailable):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
            )

    @responses.activate
    def test_no_FileWrapper_response_FileInformationUnavailable(
        self,
        monkeypatch,
    ):
        """Call to `GET .../descripor/{relative_path}` returns error response.
        """
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: None
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_files,
            json=[MOCK_TOOL_FILE],
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_rel_path,
            json=MOCK_ERROR,
            status=400,
        )
        with pytest.raises(FileInformationUnavailable):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
            )

    @responses.activate
    def test_cannot_write_to_file_OSError(
        self,
        monkeypatch,
    ):
        """Call to `GET .../descripor/{relative_path}` returns error response.
        """
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: None
        )
        monkeypatch.setattr(
            'builtins.open',
            lambda *args, **kwargs: _raise(OSError)
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_files,
            json=[MOCK_TOOL_FILE],
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_rel_path,
            json=MOCK_FILE_WRAPPER,
        )
        with pytest.raises(OSError):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
            )

    @responses.activate
    def test_success(
        self,
        monkeypatch,
    ):
        """Call completes successfully."""
        monkeypatch.setattr(
            'pathlib.Path.mkdir',
            lambda *args, **kwargs: None
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_files,
            json=[MOCK_TOOL_FILE],
        )
        responses.add(
            method=responses.GET,
            url=self.endpoint_rel_path,
            json=MOCK_FILE_WRAPPER,
        )
        with patch('builtins.open', mock_open()):
            self.cli.retrieve_files(
                out_dir=MOCK_DIR,
                type=MOCK_DESCRIPTOR,
                id=MOCK_ID,
                version_id=MOCK_ID,
            )


class TestGetHost:
    """Test domain/schema parser."""

    cli = TRSClient(uri=MOCK_TRS_URI)

    def test_trs_uri_invalid_schema(self):
        """Test host parser; TRS URI with invalid schema."""
        MOCK_TRS_URI_INVALID = f"tr://{MOCK_DOMAIN}/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_invalid_long_domain(self):
        """Provide TRS URI with long domain."""
        MOCK_TRS_URI_INVALID = (
            f"trs://{MOCK_ID * 10}.{MOCK_ID * 10}.{MOCK_ID * 10}."
            f"{MOCK_ID * 10}.{MOCK_ID * 10}/{MOCK_ID}"
        )
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_invalid_long_domain_part(self):
        """Provice TRS URI with long domain part."""
        MOCK_TRS_URI_INVALID = f"trs://{MOCK_ID * 11}.com/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_illegal_chars_in_domain(self):
        """Provide TRS URI with long domain."""
        MOCK_TRS_URI_INVALID = f"trs://3*3/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_domain_starts_with_hyphen(self):
        """Provide TRS URI with domain starting with hyphen."""
        MOCK_TRS_URI_INVALID = f"trs://-{MOCK_DOMAIN}/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_domain_ends_with_hyphen(self):
        """Provide TRS URI with domain ending with hyphen."""
        MOCK_TRS_URI_INVALID = f"trs://x.y-/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_domain_starts_with_period(self):
        """Provide TRS URI with domain starting with period."""
        MOCK_TRS_URI_INVALID = f"trs://.{MOCK_DOMAIN}/{MOCK_ID}"
        with pytest.raises(InvalidURI):
            self.cli._get_host(uri=MOCK_TRS_URI_INVALID)

    def test_trs_uri_domain_ends_with_period(self):
        """Provide TRS URI with domain ending with period."""
        MOCK_TRS_URI_VALID = f"trs://{MOCK_DOMAIN}./{MOCK_ID}"
        res = self.cli._get_host(uri=MOCK_TRS_URI_VALID)
        assert res == ("trs", MOCK_DOMAIN + ".")

    def test_trs_uri_ip(self):
        """Provide TRS URI with IP address."""
        MOCK_TRS_URI_VALID = f"trs://1.22.255.0/{MOCK_ID}"
        res = self.cli._get_host(uri=MOCK_TRS_URI_VALID)
        assert res == ("trs", "1.22.255.0")


class TestGetToolIdVersionId:
    """Test tool/version ID parser."""

    cli = TRSClient(uri=MOCK_TRS_URI)

    def test_no_input_InvalidResourceIdentifier(self):
        """No input provided."""
        with pytest.raises(InvalidResourceIdentifier):
            self.cli._get_tool_id_version_id()

    def test_invalid_tool_id_InvalidResourceIdentifier(self):
        """Invalid tool identifier provided."""
        with pytest.raises(InvalidResourceIdentifier):
            self.cli._get_tool_id_version_id(tool_id=MOCK_ID_INVALID)

    def test_invalid_version_id_InvalidResourceIdentifier(self):
        """Invalid version identifier provided."""
        with pytest.raises(InvalidResourceIdentifier):
            self.cli._get_tool_id_version_id(version_id=MOCK_ID_INVALID)

    def test_trs_uri_invalid_tool_id_InvalidResourceIdentifier(self):
        """TRS URI with invalid tool identifier."""
        MOCK_TRS_URI_INVALID = f"trs://{MOCK_ID_INVALID}/{MOCK_ID}"
        with pytest.raises(InvalidResourceIdentifier):
            self.cli._get_tool_id_version_id(tool_id=MOCK_TRS_URI_INVALID)

    def test_trs_uri_invalid_version_id_InvalidResourceIdentifier(self):
        """TRS URI with invalid version identifier."""
        MOCK_TRS_URI_INVALID = f"trs://{MOCK_ID}/{MOCK_ID_INVALID}"
        with pytest.raises(InvalidResourceIdentifier):
            self.cli._get_tool_id_version_id(tool_id=MOCK_TRS_URI_INVALID)

    def test_tool_id(self):
        """Tool identifier provided."""
        res = self.cli._get_tool_id_version_id(tool_id=MOCK_ID)
        assert res == (MOCK_ID, None)

    def test_version_id(self):
        """Version identifier provided."""
        res = self.cli._get_tool_id_version_id(version_id=MOCK_ID)
        assert res == (None, MOCK_ID)

    def test_tool_and_version_id(self):
        """Tool and version identifiers provided."""
        res = self.cli._get_tool_id_version_id(
            tool_id=MOCK_ID,
            version_id=MOCK_ID,
        )
        assert res == (MOCK_ID, MOCK_ID)

    def test_trs_uri(self):
        """Unversioned TRS URI provided."""
        res = self.cli._get_tool_id_version_id(tool_id=MOCK_TRS_URI)
        assert res == (MOCK_ID, None)

    def test_trs_uri_versioned(self):
        """Versioned TRS URI provided."""
        res = self.cli._get_tool_id_version_id(
            tool_id=MOCK_TRS_URI_VERSIONED,
        )
        assert res == (MOCK_ID, MOCK_ID)

    def test_trs_uri_versioned_override(self):
        """Versioned TRS URI and overriding version identifier provided."""
        res = self.cli._get_tool_id_version_id(
            tool_id=MOCK_TRS_URI_VERSIONED,
            version_id=MOCK_ID + MOCK_ID
        )
        assert res == (MOCK_ID, MOCK_ID + MOCK_ID)


class TestGetHeaders:
    """Test headers getter."""

    cli = TRSClient(uri=MOCK_TRS_URI)

    def test_no_args(self):
        """No arguments passed."""
        self.cli._get_headers()
        assert self.cli.headers['Accept'] == 'application/json'
        assert 'Content-Type' not in self.cli.headers
        assert 'Authorization' not in self.cli.headers

    def test_all_args(self):
        """All arguments passed."""
        self.cli.token = MOCK_TOKEN
        self.cli._get_headers(
            content_accept='text/plain',
            content_type='application/json',
            token=MOCK_TOKEN,
        )
        assert self.cli.headers['Authorization'] == f"Bearer {MOCK_TOKEN}"
        assert self.cli.headers['Accept'] == 'text/plain'
        assert self.cli.headers['Content-Type'] == 'application/json'


class TestValidateContentType:
    """Test content type validation."""

    cli = TRSClient(uri=MOCK_TRS_URI)

    def test_available_content_type(self):
        """Requested content type provided by service."""
        available_types = ['application/json']
        self.cli._validate_content_type(
            requested_type='application/json',
            available_types=available_types,
        )
        assert 'application/json' in available_types

    def test_unavailable_content_type(self):
        """Requested content type not provided by service."""
        available_types = ['application/json']
        with pytest.raises(ContentTypeUnavailable):
            self.cli._validate_content_type(
                requested_type='not/available',
                available_types=available_types,
            )


class TestSendRequestAndValidateRespose:
    """Test request sending and response validation."""

    cli = TRSClient(uri=MOCK_TRS_URI)
    endpoint = MOCK_API
    payload = {}

    def test_connection_error(self, monkeypatch):
        """Test connection error."""
        monkeypatch.setattr(
            'requests.get',
            lambda *args, **kwargs: _raise(requests.exceptions.ConnectionError)
        )
        with pytest.raises(requests.exceptions.ConnectionError):
            self.cli._send_request_and_validate_response(
                url=MOCK_API,
            )

    def test_get_str_validation(self, requests_mock):
        """Test for getter with string response."""
        requests_mock.get(self.endpoint, json=MOCK_ID)
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
            validation_class_ok=str,
        )
        assert response == MOCK_ID

    def test_get_none_validation(self, requests_mock):
        """Test for getter with `None` response."""
        requests_mock.get(self.endpoint, json=MOCK_ID)
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
            validation_class_ok=None,
        )
        assert response is None

    def test_get_model_validation(self, requests_mock):
        """Test for getter with model response."""
        requests_mock.get(self.endpoint, json=MOCK_TOOL)
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
            validation_class_ok=Tool,
        )
        assert response == MOCK_TOOL

    def test_get_list_validation(self, requests_mock):
        """Test for getter with list of models response."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL])
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
            validation_class_ok=(Tool, ),
        )
        assert response == [MOCK_TOOL]

    def test_post_validation(self, requests_mock):
        """Test for setter."""
        requests_mock.post(self.endpoint, json=MOCK_ID)
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
            method='post',
            payload=self.payload,
            validation_class_ok=str,
        )
        assert response == MOCK_ID

    def test_get_success_invalid(self, requests_mock):
        """Test for 200 response that fails validation."""
        requests_mock.get(self.endpoint, json=MOCK_TOOL)
        with pytest.raises(InvalidResponseError):
            self.cli._send_request_and_validate_response(
                url=MOCK_API,
                validation_class_ok=Error,
            )

    def test_error_response(self, requests_mock):
        """Test for valid error response."""
        requests_mock.get(self.endpoint, json=MOCK_ERROR, status_code=400)
        response = self.cli._send_request_and_validate_response(
            url=MOCK_API,
        )
        assert response == MOCK_ERROR

    def test_error_response_invalid(self, requests_mock):
        """Test for error response that fails validation."""
        requests_mock.get(self.endpoint, json=MOCK_ERROR, status_code=400)
        with pytest.raises(InvalidResponseError):
            self.cli._send_request_and_validate_response(
                url=MOCK_API,
                validation_class_error=Tool,
            )

    def test_invalid_http_method(self, requests_mock):
        """Test for invalid HTTP method."""
        requests_mock.get(self.endpoint, json=[MOCK_TOOL_CLASS])
        with pytest.raises(AttributeError):
            self.cli._send_request_and_validate_response(
                url=MOCK_API,
                method='non_existing',
                payload=self.payload,
            )
