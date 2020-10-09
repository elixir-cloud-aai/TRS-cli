"""Class implementing TRS client."""

import json
import logging
from pathlib import Path
import re
import socket
import sys
from typing import (Dict, List, Optional, Tuple, Union)
import urllib3
from urllib.parse import quote

import pydantic
from pydantic.main import ModelMetaclass
import requests

from trs_cli.errors import (
    exception_handler,
    ContentTypeUnavailable,
    FileInformationUnavailable,
    InvalidURI,
    InvalidPayload,
    InvalidResourceIdentifier,
    InvalidResponseError,
)
from trs_cli.models import (
    Error,
    FileType,
    FileWrapper,
    ToolFile,
    Tool,
    ToolClass,
    ToolClassRegister,
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
        self.headers = {}
        logger.info(f"Instantiated client for: {self.uri}")

    def post_tool_class(
        self,
        payload: Dict,
        accept: str = 'application/json',
        token: Optional[str] = None,
    ) -> str:
        """Register a tool class.

        Arguments:
            payload: Tool class data.
            accept: Requested content type.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.

        Returns:
            ID of registered TRS toolClass in case of a `200` response, or an
            instance of `Error` for all other responses.
        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidPayload: The object data payload could not
                be validated against the API schema.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        self._validate_content_type(
            requested_type=accept,
            available_types=['application/json'],
        )
        self._get_headers(
            content_accept=accept,
            content_type='application/json',
            token=token,
        )

        # build request URL
        url = f"{self.uri}/toolClasses"
        logger.info(f"Connecting to '{url}'...")

        # validate payload
        try:
            ToolClassRegister(**payload).dict()
        except pydantic.ValidationError:
            raise InvalidPayload(
                "The tool class data could not be validated against API "
                "schema."
            )

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            method='post',
            payload=payload,
        )
        logger.info(
            "Registered tool class"
        )
        return response  # type: ignore

    def get_tool(
        self,
        id: str,
        accept: str = 'application/json',
        token: Optional[str] = None,
    ) -> Union[Tool, Error]:
        """Retrieve tool with the specified identifier.

        Arguments:
            tool_id: Implementation-specific TRS identifier hostname-based
               TRS URI pointing to a given tool
            accept: Requested content type.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.

        Returns:
            Unmarshalled TRS response as either an instance of `Tool`
            in case of a `200` response, or an instance of `Error` for all
            other JSON reponses.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        self._validate_content_type(
            requested_type=accept,
            available_types=['application/json', 'text/plain'],
        )
        self._get_headers(
            content_accept=accept,
            token=token,
        )

        # get/sanitize tool identifier
        _id, _ = self._get_tool_id_version_id(tool_id=id)

        # build request URL
        url = f"{self.uri}/tools/{_id}"
        logger.info(f"Connecting to '{url}'...")

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            validation_class_200=Tool,
        )
        logger.info(
            "Retrieved tool"
        )
        return response  # type: ignore

    def get_descriptor(
        self,
        type: str,
        id: str,
        version_id: Optional[str] = None,
        accept: str = 'application/json',
        token: Optional[str] = None
    ) -> Union[FileWrapper, Error]:
        """Retrieve the file wrapper for the primary descriptor of a specified
        tool version and descriptor type.

        Arguments:
            type: The output type of the descriptor. Plain types return
                the bare descriptor while the "non-plain" types return a
                descriptor wrapped with metadata. Allowable values include
                "CWL", "WDL", "NFL", "GALAXY", "PLAIN_CWL", "PLAIN_WDL",
                "PLAIN_NFL", "PLAIN_GALAXY".
            id: A unique identifier of the tool, scoped to this registry OR
                a TRS URI. If a TRS URI is passed and includes the version
                identifier, passing a `version_id` is optional. For more
                information on TRS URIs, cf.
                https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
            version_id: Identifier of the tool version, scoped to this
                registry. It is optional if a TRS URI is passed and includes
                version information. If provided nevertheless, then the
                `version_id` retrieved from the TRS URI is overridden.
            accept: Requested content type.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.

        Returns:
            Unmarshalled TRS response as either an instance of `FileWrapper` in
            case of a `200` response, or an instance of `Error` for all other
            JSON reponses.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        self._validate_content_type(
            requested_type=accept,
            available_types=['application/json', 'text/plain'],
        )
        self._get_headers(
            content_accept=accept,
            token=token,
        )

        # get/sanitize tool and version identifiers
        _id, _version_id = self._get_tool_id_version_id(
            tool_id=id,
            version_id=version_id,
        )

        # build request URL
        url = (
            f"{self.uri}/tools/{_id}/versions/{_version_id}/{type}/"
            "descriptor"
        )
        logger.info(f"Connecting to '{url}'...")

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            validation_class_200=FileWrapper,
        )
        logger.info(
            "Retrieved descriptor"
        )
        return response  # type: ignore

    def get_descriptor_by_path(
        self,
        type: str,
        path: str,
        id: str,
        version_id: Optional[str] = None,
        is_encoded: bool = False,
        accept: str = 'application/json',
        token: Optional[str] = None
    ) -> Union[FileWrapper, Error]:
        """Retrieve the file wrapper for an indicated file for the specified
        tool version and descriptor type.

        Arguments:
            type: The output type of the descriptor. Plain types return
                the bare descriptor while the "non-plain" types return a
                descriptor wrapped with metadata. Allowable values include
                "CWL", "WDL", "NFL", "GALAXY", "PLAIN_CWL", "PLAIN_WDL",
                "PLAIN_NFL", "PLAIN_GALAXY".
            path: Path, including filename, of descriptor or associated file
                relative to the primary descriptor file.
            id: A unique identifier of the tool, scoped to this registry OR
                a TRS URI. If a TRS URI is passed and includes the version
                identifier, passing a `version_id` is optional. For more
                information on TRS URIs, cf.
                https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris
            version_id: Identifier of the tool version, scoped to this
                registry. It is optional if a TRS URI is passed and includes
                version information. If provided nevertheless, then the
                `version_id` retrieved from the TRS URI is overridden.
            is_encoded: Value of `path` is already percent/URL-encoded.
            accept: Requested content type.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.

        Returns:
            Unmarshalled TRS response as either an instance of `FileWrapper` in
            case of a `200` response, or an instance of `Error` for all other
            JSON reponses.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        self._validate_content_type(
            requested_type=accept,
            available_types=['application/json', 'text/plain'],
        )
        self._get_headers(
            content_accept=accept,
            token=token,
        )

        # get/sanitize tool and version identifiers
        _id, _version_id = self._get_tool_id_version_id(
            tool_id=id,
            version_id=version_id,
        )

        # build request URL
        _path = path if is_encoded else quote(path, safe='')
        url = (
            f"{self.uri}/tools/{_id}/versions/{_version_id}/{type}/"
            f"descriptor/{_path}"
        )
        logger.info(f"Connecting to '{url}'...")

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            validation_class_200=FileWrapper,
        )
        logger.info(
            "Retrieved descriptor"
        )
        return response  # type: ignore

    def get_files(
        self,
        type: str,
        id: str,
        version_id: Optional[str] = None,
        format: Optional[str] = None,
        token: Optional[str] = None
    ) -> Union[List[ToolFile], Error]:
        """Retrieve file information for the specified tool version and
        descriptor type.

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
            Unmarshalled TRS response as either an instance of `ToolFile` in
            case of a `200` response, or an instance of `Error` for all other
            JSON reponses.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        if format is None:
            query_format = ""
            accept = 'application/json'
        elif format == 'zip':
            query_format = "?format=zip"
            accept = 'application/zip'
        else:
            raise ContentTypeUnavailable(
                "Only 'zip' is allowed for parameter 'format'; omit query"
                "parameter to request JSON instead"
            )
        self._get_headers(
            content_accept=accept,
            token=token,
        )

        # get/sanitize tool and version identifiers
        _id, _version_id = self._get_tool_id_version_id(
            tool_id=id,
            version_id=version_id,
        )

        # build request URL
        url = (
            f"{self.uri}/tools/{_id}/versions/{_version_id}/{type}/"
            f"files{query_format}"
        )
        logger.info(f"Connecting to '{url}'...")

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            validation_class_200=(ToolFile, ),
        )
        logger.info(
            "Retrieved files"
        )
        return response  # type: ignore

    def get_tool_classes(
        self,
        accept: str = 'application/json',
        token: Optional[str] = None
    ) -> Union[List[ToolClass], Error]:
        """Retrieve tool classes.

        Arguments:
            accept: Requested content type.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.

        Returns:
            Unmarshalled TRS response as either a list of `ToolClass` objects
            in case of a `200` response, or an instance of `Error` for all
            other JSON reponses.

        Raises:
            requests.exceptions.ConnectionError: A connection to the provided
                TRS instance could not be established.
            trs_cli.errors.InvalidResponseError: The response could not be
                validated against the API schema.
        """
        # validate requested content type and get request headers
        self._validate_content_type(
            requested_type=accept,
            available_types=['application/json', 'text/plain'],
        )
        self._get_headers(
            content_accept=accept,
            token=token,
        )

        # build request URL
        url = f"{self.uri}/toolClasses"
        logger.info(f"Connecting to '{url}'...")

        # send request
        response = self._send_request_and_validate_response(
            url=url,
            validation_class_200=(ToolClass, ),
        )
        logger.info(
            "Retrieved tool classes"
        )
        return response  # type: ignore

    def retrieve_files(
        self,
        out_dir: Union[str, Path],
        type: str,
        id: str,
        version_id: Optional[str] = None,
        is_encoded: bool = False,
        token: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """Write tool version file contents for a given descriptor type to
        files.

        Arguments:
            out_dir: Directory to write requested files to. Will be attempted
                to create if it does not exist.
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
            is_encoded: Values or relative paths of files are already
                percent/URL-encoded.

        Returns:
            Dictionary of `FileType` enumerator values (e.g., `TEST_FILE`,
            `PRIMARY_DESCRIPTOR`) as keys and a list of paths, relative to
            `out_dir` as values.
        """
        # if not exists, try to create output directory
        out_dir = Path(out_dir)
        try:
            Path(out_dir).mkdir(parents=True, exist_ok=True)
        except OSError:
            raise OSError("Could not create output directory")

        # get file information
        files = self.get_files(
            type=type,
            id=id,
            version_id=version_id,
            token=token,
        )
        if isinstance(files, Error):
            raise FileInformationUnavailable(
                "File information unavailable"
            )

        # get path of primary descriptor
        paths_by_type = {item.value: [] for item in FileType}
        for _file in files:
            if _file.path is not None:
                paths_by_type[_file.file_type.value].append(_file.path)

        # get file wrappers
        file_wrappers = {}
        for _f in files:
            if not hasattr(_f, 'path') or _f.path is None:
                raise FileInformationUnavailable(
                    f"Path information unavailable for file object: {_f}"
                )
            file_wrapper = self.get_descriptor_by_path(
                type=type,
                path=_f.path,
                id=id,
                version_id=version_id,
                is_encoded=is_encoded,
                token=token,
            )
            if not isinstance(file_wrapper, FileWrapper):
                raise FileInformationUnavailable(
                    "Content unavailable for file at path '{_f.path}'"
                )
            file_wrappers[_f.path] = file_wrapper.content

        # write contents to files
        for path, content in file_wrappers.items():
            out_path = out_dir / path
            try:
                with open(out_path, "w") as _fp:
                    _fp.write(content)
            except OSError:
                raise OSError(f"Could not write file '{str(out_path)}'")

        return paths_by_type

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
            Tuple of validated, percent-encoded tool and version identifiers,
            respectively; if no `version_id` was supplied OR an unversioned TRS
            URI was passed to `tool_id`, the second item of the tuple will be
            set to `None`; likewise, if not `tool_id` was provided, the first
            item of the tuple will be set to `None`.

        Raises:
            trs_cli.errors.InvalidResourceIdentifier: Neither `tool_id` nor
                `version_id` were supplied OR the tool or version
                identifier could not be parsed.
        """
        ret_tool_id: Optional[str] = None
        ret_version_id: Optional[str] = None

        if tool_id is None and version_id is None:
            raise InvalidResourceIdentifier(
                "No TRS URI, tool or version identifier supplied"
            )

        if tool_id is not None:
            match = re.search(self._RE_TRS_URI_OR_TOOL_ID, tool_id, re.I)
            if match is None:
                raise InvalidResourceIdentifier(
                    "The provided tool identifier is invalid"
                )
            ret_tool_id = match.group('tool_id')
            ret_version_id = match.group('version_id')

        if version_id is not None:
            match = re.search(self._RE_VERSION_ID, version_id, re.I)
            if match is None:
                raise InvalidResourceIdentifier(
                    "The provided version identifier is invalid"
                )
            ret_version_id = match.group('version_id')

        if ret_tool_id is not None:
            ret_tool_id = quote(ret_tool_id, safe='')
        if ret_version_id is not None:
            ret_version_id = quote(ret_version_id, safe='')

        return (ret_tool_id, ret_version_id)

    def _get_headers(
        self,
        content_accept: str = 'application/json',
        content_type: Optional[str] = None,
        token: Optional[str] = None,
    ) -> None:
        """Build dictionary of request headers.

        Arguments:
            content_accept: Requested MIME/content type.
            content_type: Type of content sent with the request.
            token: Bearer token for authentication. Set if required by TRS
                implementation and if not provided when instatiating client or
                if expired.
        """
        self.headers['Accept'] = content_accept
        if content_type:
            self.headers['Content-Type'] = content_type
        if token is not None:
            self.token = token
            self.headers['Authorization'] = f"Bearer {self.token}"

    def _validate_content_type(
        self,
        requested_type: str,
        available_types: List[str] = ['application/json'],
    ) -> None:
        """Ensure that content type is among content types provided by the
        service.

        Arguments:
            requested_type: Requested MIME/content type.
            available_types: Content types provided by the service for a given
                endpoint.

        Raises:
            ContentTypeUnavailable: The service does not provide the requested
                content type.
        """
        if requested_type not in available_types:
            raise ContentTypeUnavailable(
                "Requested content type not provided by the service"
            )

    def _send_request_and_validate_response(
        self,
        url: str,
        validation_class_200: Optional[
            Union[ModelMetaclass, Tuple[ModelMetaclass]]
        ] = None,
        validation_class_error: ModelMetaclass = Error,
        method: str = 'get',
        payload: Optional[Dict] = None,
    ) -> Union[str, ModelMetaclass, List[ModelMetaclass]]:
        """Send a HTTP equest, validate the response and handle potential
        exceptions.

        Arguments:
            url: The URL to send the request to.
            validation_class_200: Type/class to be used to validate a 200
                response. Either a Pydantic model, a tuple with a Pydantic
                model as the only item (for list responses), or `None` (for
                string responses).
            validation_class_error: Pydantic model to be used to validate
                non-200 responses.
            method: HTTP method to use for the request.

        Returns:
            Unmarshalled response.
        """
        # Process parameters
        validation_type = "model"
        if isinstance(validation_class_200, tuple):
            validation_class_200 = validation_class_200[0]
            validation_type = "list"
        elif validation_class_200 is None:
            validation_type = "str"
        try:
            request_func = eval('.'.join(['requests', method]))
        except AttributeError as e:
            raise AttributeError("Illegal HTTP method provided.") from e

        # Compile request arguments
        kwargs = {
            'url': url,
            'headers': self.headers,
        }
        if payload is not None:
            kwargs['json'] = payload

        # Send request and manage response
        try:
            response = request_func(**kwargs)
        except (
            requests.exceptions.ConnectionError,
            socket.gaierror,
            urllib3.exceptions.NewConnectionError,
        ):
            raise requests.exceptions.ConnectionError(
                "Could not connect to API endpoint"
            )
        if not response.status_code == 200:
            try:
                logger.warning("Received error response")
                return validation_class_error(**response.json())
            except (
                json.decoder.JSONDecodeError,
                pydantic.ValidationError,
            ):
                raise InvalidResponseError(
                    "Response could not be validated against API schema"
                )
        else:
            try:
                if validation_type == "list":
                    return [
                        validation_class_200(**obj) for obj in response.json()
                    ]
                elif validation_type == "str":
                    return str(response.json())
                else:
                    return validation_class_200(**response.json())
            except (
                json.decoder.JSONDecodeError,
                pydantic.ValidationError,
            ):
                raise InvalidResponseError(
                    "Response could not be validated against API schema"
                )
