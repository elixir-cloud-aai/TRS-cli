"""Unit tests for TRS client."""

import pytest

from trs_cli.client import TRSClient
from trs_cli.errors import (
    InvalidURI,
    InvalidResourceIdentifier,
)

MOCK_DOMAIN = "x.y.z"
MOCK_HOST = f"https://{MOCK_DOMAIN}"
MOCK_ID = "123456"
MOCK_ID_INVALID = "N0T VAL!D"
MOCK_TRS_URI = f"trs://{MOCK_DOMAIN}/{MOCK_ID}"
MOCK_TRS_URI_VERSIONED = f"trs://{MOCK_DOMAIN}/{MOCK_ID}/versions/{MOCK_ID}"
MOCK_PORT = 4434
MOCK_BASE_PATH = "a/b/c"
MOCK_TOKEN = "MyT0k3n"


class TestTRSClientConstructor:
    """Test TRSClient() construction."""

    def test_invidiual_parts(self):
        """Provide invidiual parts."""
        cli = TRSClient(
            uri=MOCK_HOST,
            port=MOCK_PORT,
            base_path=MOCK_BASE_PATH,
            use_http=True,
            token=MOCK_TOKEN,
        )
        assert cli.uri == f"https://{MOCK_DOMAIN}:{MOCK_PORT}/{MOCK_BASE_PATH}"

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
    """Test too/version ID parser."""

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
