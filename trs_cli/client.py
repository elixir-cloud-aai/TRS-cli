"""Class implementing TRS client."""

import logging
import re
import sys
from typing import (Dict, Optional, Tuple)

from trs_cli.errors import (
    exception_handler,
    InvalidURI,
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
    _RE_DOMAIN = rf"({_RE_DOMAIN_PART}\.)+{_RE_DOMAIN_PART}\.?"
    _RE_TRS_ID = r'\S+'  # TODO: update to account for versioned TRS URIs
    _RE_HOST = rf"^(?P<schema>trs|http|https):\/\/(?P<host>{_RE_DOMAIN})\/?"

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
