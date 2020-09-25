"""Class implementing TRS client."""

import logging
import re
import sys
import requests
import socket
from typing import (Dict, Optional, Tuple)
from urllib.parse import quote
import urllib3

from trs_cli.errors import (
    exception_handler,
    InvalidURI,
    InvalidResourcedentifier,
)

logger = logging.getLogger(__name__)
sys.excepthook = exception_handler


class TRSClient():
    """Client to communicate with a GA4GH TRS instance. Supports additional
    endpoints defined in TRS-Filer
    (https://github.com/elixir-cloud-aai/trs-filer).

    Arguments:
        uri: Either the base URI of the TRS instance to connect to in either
            'https' or 'http' schema (note that fully compliant TRS instances
            will use 'https' exclusively), e.g., `https://my-trs.app`, OR a
            hostname-based TRS URI, cf.
            https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
        port: Override default port at which the TRS instance can be accessed.
            Only required for TRS instances that are not fully spec-compliant,
            as the default port is defined in the TRS documentation, cf.
            https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
        base-path: Override default path at which the TRS API is accessible at
            the given TRS instance. Only required for TRS instances that are
            not fully spec-compliant, as the default port is defined in the TRS
            documentation, cf.
            https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
        use_http: Set the URI schema of the TRS instance to `http` instead of
            `https`when a TRS URI was provided to `uri`.
        token: Bearer token to send along with TRS API requests. Set if
            required by TRS implementation. Alternatively, specify in API
            endpoint access methods.

    Attributes:
        uri: URI to TRS endpoints, built from `uri`, `port` and `base_path`,
            e.g.,"https://my-trs.app:443/ga4gh/trs/v2".
        token: Bearer token for gaining access to TRS endpoints.
        headers: Dictionary of request headers.
    """
    # set regular expressions as private class variables
    _RE_DOMAIN_PART = r'[a-z0-9]([a-z0-9-]{1,61}[a-z0-9]?)?'
    _RE_DOMAIN = rf"({_RE_DOMAIN_PART}\.?)+{_RE_DOMAIN_PART}\.?"
    _RE_TRS_ID = r'\S+'  # TODO: update to account for versioned TRS URIs
    _RE_HOST = rf"^(?P<schema>trs|http|https):\/\/(?P<host>{_RE_DOMAIN})\/?"
    _RE_TRS_TOOL_UID = r"[a-z0-9]{6}"
    _RE_TOOL_ID = rf"^(trs:\/\/{_RE_DOMAIN}\/)?(?P<tool_id>" \
        rf"{_RE_TRS_TOOL_UID})(\/versions\/)?(?P<tool_version_id>.*)?"

    def __init__(
        self,
        uri: str,
        port: int = None,
        base_path: str = 'ga4gh/trs/v2',
        use_http: bool = False,
        token: Optional[str] = None,
    ) -> None:
        """Class constructor."""
        schema, host = self._get_host(uri)
        if schema == 'trs':
            schema = 'http' if use_http else 'https'
        if port is None:
            port = 80 if schema == 'http' else 443
        self.uri = f"{schema}://{host}:{port}/{base_path}"
        self.token = token
        self.headers = self._get_headers()
        logger.info(f"Instantiated client for: {self.uri}")

    # TODO: implement methods to connect to various endpoints below, e.g.,:
    #
    # def get_tools(self) -> List:
    # """Docstring"""
    #
    # Check DRS-cli repo for examples

    def _get_tool_version(
        self,
        tool_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """
        Return sanitized tool and/or version identifiers or extract them from
        a TRS URI.

        Arguments:
            tool_id: Implementation-specific TRS tool identifier OR TRS URI
                pointing to a given tool, cf.
                https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
                Note that if a TRS URI is passed, only the TRS identifier parts
                (tool and version) will be evaluated. To reset the hostname,
                create a new client with the `TRSClient()` constructor.
            version_id: Implementation-specific TRS version identifier; if
                provided, will take precedence over any version identifier
                extracted from a versioned TRS URI passed to `tool_id`

            Returns:
                Tuple of validated, percent-encoded tool and version
                identifiers, respectively; if no `version_id` was supplied OR
                an unversioned TRS URI was passed to `tool_id`, the second
                item of the tuple will be set to `None`; likewise, if not
                `tool_id` was provided, the first item of the tuple will
                be set to `None`.

            Raises:
                drs_cli.errors.InvalidResourcedentifier: input tool identifier
                    cannot be parsed.
        """
        if not tool_id and not version_id:
            raise InvalidResourcedentifier(
                "Tool_id and version_id not provided"
            )

        re_tool_id_regex, re_version_id = self._get_tool_and_version_id(
            tool_id=tool_id)

        if tool_id and not version_id:
            if re_version_id:
                version_id = re_version_id
                url = f"{self.uri}/tools/{re_tool_id_regex}" \
                    f"/versions/{version_id}"
            else:
                url = f"{self.uri}/tools/{re_tool_id_regex}"
        elif tool_id and version_id:
            url = f"{self.uri}/tools/{re_tool_id_regex}/versions/{version_id}"

        logger.info(f"Request URL: {url}")

        try:
            response = requests.get(
                url=url,
                headers=self.headers,
            )
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint."
            )
        if not response.status_code == 200:
            raise InvalidResourcedentifier(
                "Input tool identifier cannot be parsed"
            )

        if not version_id:  # If version_id is '' i.e NA according to regex
            version_id = None

        return [re_tool_id_regex, version_id]

    def _get_headers(self) -> Dict:
        """Build dictionary of request headers.

        Returns:
            A dictionary of request headers
        """
        headers: Dict = {
            'Content-type': 'application/json',
        }
        if self.token:
            headers['Authorization'] = 'Bearer ' + self.token
        return headers

    def _get_host(
        self,
        uri: str,
    ) -> Tuple[str, str]:
        """Extract URI schema and domain or IP from HTTP, HTTPS or TRS URI.

        Arguments:
            uri: HTTP or HTTPS URI pointing to the root domain/IP of a TRS
                instance OR a hostname-based TRS URI to a given tool, cf.
                https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
                Anything after a slash following the domain/IP will be ignored.

        Returns:
            Tuple of URI schema (e.g., 'https', 'trs') and host domain or IP
            (e.g., 'my-trs.app', '0.0.0.0').

        Raises:
            trs_cli.errors.InvalidURI: input URI cannot be parsed.

        Examples:
           >>> TRSClient.get_host(uri="https://my-trs.app/will-be-ignored")
           ('https', 'my-trs.app')
           >>> TRSClient.get_host(uri="trs://my-trs.app/MyT00l")
           ('trs', 'my-trs.app')
        """
        match = re.search(self._RE_HOST, uri, re.I)
        if match:
            schema = match.group('schema')
            host = match.group('host').rstrip('\\')
            if len(host) > 253:
                raise InvalidURI
            return (schema, host)
        else:
            raise InvalidURI

    def _get_tool_and_version_id(
        self,
        tool_id: str,
    ) -> str:
        """
        Arguments:
            tool_id: Implementation-specific TRS identifier OR hostname-based
               TRS URI pointing to a given object.
        Returns:
            Validated, percent-encoded tool id and version id.
        """
        match = re.search(self._RE_TOOL_ID, tool_id, re.I)
        return quote(string=match.group('tool_id'), safe=''), \
            quote(string=match.group('tool_version_id'), safe='')
