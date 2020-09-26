"""Class implementing TRS client."""

import json
import logging
import pydantic
import re
import requests
import socket
import sys
from typing import (Dict, Optional, Tuple, Union)
import urllib3
from urllib.parse import quote

from trs_cli.errors import (
    exception_handler,
    InvalidURI,
    InvalidResourceIdentifier,
    InvalidResponseError,
    InvalidContentType
)
from trs_cli.models import Error, ToolFile  # noqa: F401

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
    _RE_DOMAIN_PART = r'[a-z0-9]([a-z0-9-]{,61}[a-z0-9])?'
    _RE_DOMAIN = rf"({_RE_DOMAIN_PART}\.)+{_RE_DOMAIN_PART}\.?"
    _RE_TRS_ID = r'([a-z0-9-_~\.%#]+)'
    _RE_VERSION_ID = rf"^(?P<version_id>{_RE_TRS_ID})$"
    _RE_HOST = (
        rf"^(?P<schema>trs|http|https):\/\/(?P<host>{_RE_DOMAIN})(\/\S+)?$"
    )
    _RE_TRS_URI_OR_TOOL_ID = (
        rf"^(trs:\/\/{_RE_DOMAIN}\/)?(?P<tool_id>{_RE_TRS_ID})"
        rf"(\/versions\/(?P<version_id>{_RE_TRS_ID}))?$"
    )

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

    def get_files(
        self,
        type: str,
        id: str,
        version_id: Optional[str] = None,
        format: Optional[str] = None,
        token: Optional[str] = None
    ) -> Union[ToolFile, Error]:
        """Get the tool files for the specified tool.
        Arguments:
            type: The output type of the descriptor. Plain types return
                the bare descriptor while the "non-plain" types return a
                descriptor wrapped with metadata. Allowable values include
                "CWL", "WDL", "NFL", "GALAXY", "PLAIN_CWL", "PLAIN_WDL",
                "PLAIN_NFL", "PLAIN_GALAXY".
            id: A unique identifier of the tool, scoped to this registry OR
                a hostname-based TRS URI. If TRS URIs include the version
                information, passing a `version_id` is optional.
            version_id: An optional identifier of the tool version, scoped
                to this registry. It is optional if version info is included
                in the TRS URI. If passed, then the existing `version_id`
                retreived from the TRS URI is overridden.
            format: Returns a zip file of all files when format=zip is
            specified.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.
        Returns:
            Unmarshalled TRS response as either an instance of
            `ToolFile` in case of a `200` response, or an instance of
            `Error` for all other JSON reponses.
        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        id, version_id = self._get_tool_id_version_id(
            tool_id=id,
            version_id=version_id
        )
        if format is not None:
            if format not in ['json', 'zip']:
                url = f"{self.uri}/tools/{id}/versions/{version_id}/" \
                    f"{type}/files"
                raise InvalidContentType
            else:
                if format == 'zip':
                    self._get_headers_zip()
                elif format == 'json':
                    self._get_headers()
                url = f"{self.uri}/tools/{id}/versions/{version_id}/{type}/" \
                      f"files?format={format}"
        else:
            self._get_headers()

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
            try:
                response_val = Error(**response.json())
            except (
                json.decoder.JSONDecodeError,
                pydantic.ValidationError,
            ):
                raise InvalidResponseError(
                    "Response could not be validated against API schema."
                )
            logger.warning("Received error response.")
        else:
            try:
                response_val = ToolFile(**response.json())
            except pydantic.ValidationError:
                raise InvalidResponseError(
                    "Response could not be validated against API schema."
                )
            logger.info(
                f"Retrieved files of type '{type}' for tool '{id}',"
                f"version '{version_id}'."
            )

        return response_val

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

    def _get_headers_zip(self) -> Dict:
        """Build dictionary of request headers.

        Returns:
            A dictionary of request headers
        """
        headers: Dict = {
            'Content-type': 'application/zip',
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
        if match is not None:
            schema = match.group('schema')
            host = match.group('host').rstrip('\\')
            if len(host) > 253:
                raise InvalidURI
            return (schema, host)
        else:
            raise InvalidURI

    def _get_tool_id_version_id(
        self,
        tool_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str]]:
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
                trs_cli.errors.InvalidResourceIdentifier: Neither `tool_id` nor
                    `version_id` were supplied OR the tool or version
                    identifier could not be parsed.
        """
        ret_tool_id: Optional[str] = None
        ret_version_id: Optional[str] = None

        if tool_id is None and version_id is None:
            logger.error("No TRS URI, tool or version identifier supplied.")
            raise InvalidResourceIdentifier

        if tool_id is not None:
            match = re.search(self._RE_TRS_URI_OR_TOOL_ID, tool_id, re.I)
            if match is None:
                logger.error("The provided tool identifier is invalid.")
                raise InvalidResourceIdentifier
            ret_tool_id = match.group('tool_id')
            ret_version_id = match.group('version_id')

        if version_id is not None:
            match = re.search(self._RE_VERSION_ID, version_id, re.I)
            if match is None:
                logger.error("The provided version identifier is invalid.")
                raise InvalidResourceIdentifier
            ret_version_id = match.group('version_id')

        if ret_tool_id is not None:
            ret_tool_id = quote(ret_tool_id, safe='')
        if ret_version_id is not None:
            ret_version_id = quote(ret_version_id, safe='')

        return (ret_tool_id, ret_version_id)
