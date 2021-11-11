# TRS-cli

[![License][badge-license]][badge-url-license]
[![Build_status][badge-build-status]][badge-url-build-status]
[![Docs][badge-docs]][badge-url-docs]
[![Coverage][badge-coverage]][badge-url-coverage]
[![GitHub_tag][badge-github-tag]][badge-url-github-tag]
[![PyPI_release][badge-pypi]][badge-url-pypi]

Client for implementations of the [Global Alliance for Genomics and
Health (GA4GH)][res-ga4gh] [Tool Registry Service API][res-ga4gh-trs] schema,
including support for additional endpoints defined in [ELIXIR Cloud &
AAI's][res-elixir-cloud] generic [TRS-Filer][res-elixir-cloud-trs-filer] TRS
implementation.

The TRS API version underlying the client can be found
[here][res-ga4gh-trs-version].

TRS-cli has so far been succesfully tested with the
[TRS-Filer][res-elixir-cloud-trs-filer] and
[WorkflowHub][res-eosc-workflow-hub] TRS implementations. WorkflowHub's public
TRS API endpoint can be found here: <https://dev.workflowhub.eu/ga4gh/trs/v2>

## Table of Contents

* [Usage](#usage)
  * [Configure client class](#configure-client-class)
  * [Create client instance](#create-client-instance)
  * [Access methods](#access-methods)
  * [Authorization](#authorization)
* [API documentation](#api-documentation)
* [Installation](#installation)
  * [Via package manager](#via-package-manager)
  * [Manual installation](#manual-installation)
* [Contributing](#contributing)
* [Versioning](#versioning)
* [License](#license)
* [Contact](#contact)

## Usage

To use the client import it as follows in your Python code after
[installation](#Installation):

```py
from trs_cli import TRSClient
```

### Configure client class

It is possible to configure the `TRSClient` class with the `.config()` class
method. The following configuration parameters are available:

| Parameter | Type | Default | Description |
| --- | --- | ---- | --- |
| `debug` | `bool` | `False` | If set, the exception handler prints tracebacks for every exception encountered. |
| `no_validate` | `bool` | `False` | If set, responses JSON are not validated against the TRS API schemas. In that case, unserialized `response` objects are returned. Set this flag if the TRS implementation you are working with is not fully compliant with the TRS API specification. |

Example:

```py
from trs_cli import TRSClient

TRSClient.config(debug=True, no_validate=True)
```

> Note that as a _class method_, the `.config()` method will affect _all_
> client instances, including existing ones.

### Create client instance

#### Via TRS hostname

A client instance can be created by specifying the domain name of a TRS
instance, including the URL schema:

```py
from trs_cli import TRSClient

client = TRSClient(uri="https://my-trs.app")
# Client instantiated for URL: https://my-trs.app:443/ga4gh/trs/v2
```

Fully [spec-compliant][res-ga4gh-trs] TRS implementations will always be
available at `https` URLs, served at port `443` and at the base path
`ga4gh/trs/v2`. However, to allow the client to be used against development
versions of TRS implementations, `http` URLs are supported as well (default
port `80`), and the port and base path at which the API endpoints are served
can be overridden with the `port` and `base_path` arguments:

```py
from trs_cli import TRSClient

client = TRSClient(
    uri="http://my-trs.app",
    port=8080,
    base_path="my/api/route",
)
# Client instantiated for URL: http://my-trs.app:8080/my/api/route
```

#### Via TRS URI

Clients can also be created by passing a [hostname-based TRS
URI][res-ga4gh-trs-uri]:

```py
from trs_cli import TRSClient

client = TRSClient(uri="trs://my-trs.app/SOME_TOOL")
# Client instantiated for URL: https://my-trs.app:443/ga4gh/trs/v1
```

> **NOTE:** Only the hostname part of the TRS URI is evaluated, not the tool
> ID.

Port and base path can be overridden as described above. In addition, the
client constructor also defines the `use_http` flag, which instantiates a
client for an `http` URL when a TRS URI is passed. The flag has no effect
when a TRS hostname URL is provided instead of a TRS URI:

```py
from trs_cli import TRSClient

client = TRSClient(
    uri="trs://my-trs.app/SOME_TOOL",
    use_http=True,
)
# Client instantiated for URL: http://my-trs.app:443/ga4gh/trs/v1
```

### Access methods

> **NOTES:**
>  
> * All endpoint access methods require a [client
>   instance](#create-client-instance).
> * For accessing endpoints that require authorization, see the
>   [dedicated section](#authorization).
> * Responses that do not return the tool ID as a single string return
>   [Pydantic][res-pydantic] models instead. If dictionaries are preferred
>   instead, they can be obtained with `response.dict()`. See the [Pydantic
>   export documentation][res-pydantic-docs-export] for further details.
> * See the [API documentation][docs-api] for further details on each access
>   method.

#### Endpoints as specified in the TRS API

Access methods for each [Tool Registry Service API][res-ga4gh-trs] endpoint
are available:

| Method | Endpoint | Description |
| --- | --- | --- |
| [`.get_tool_classes()`][docs-api-get_tool_classes] | `GET ​/toolClasses` | List all tool types |
| [`.get_tools()`][docs-api-get_tools] | `GET ​/tools` | List all tools |
| [`.get_tool()`][docs-api-get_tool] | `GET ​/tools​/{id}` | List one specific tool, acts as an anchor for self references |
| [`.get_versions()`][docs-api-get_versions] | `GET ​/tools​/{id}​/versions` | List versions of a tool |
| [`.get_version()`][docs-api-get_version] | `GET ​/tools​/{id}​/versions​/{version_id}` | List one specific tool version, acts as an anchor for self references |
| [`.get_containerfiles()`][docs-api-get_containerfiles] | `GET ​/tools​/{id}​/versions​/{version_id}​/containerfile` | Get the container specification(s) for the specified image. |
| [`.get_descriptor()`][docs-api-get_descriptor] | `GET ​/tools​/{id}​/versions​/{version_id}​/{type}​/descriptor` | Get the tool descriptor for the specified tool |
| [`.get_descriptor_by_path()`][docs-api-get_descriptor_by_path] | `GET ​/tools​/{id}​/versions​/{version_id}​/{type}​/descriptor​/{relative_path}` | Get additional tool descriptor files relative to the main file |
| [`.get_files()`][docs-api-get_files] | `GET ​/tools​/{id}​/versions​/{version_id}​/{type}​/files` | Get a list of objects that contain the relative path and file type |
| [`.get_tests()`][docs-api-get_tests] | `GET ​/tools​/{id}​/versions​/{version_id}​/{type}​/tests` | Get a list of test JSONs |
| [`.get_service_info()`][docs-api-get_service_info] | `GET ​/service-info` | Show information about this service. It is assumed that removing this endpoint from a URL will result in a valid URL to query against |

#### TRS-Filer-specific endpoints

In addition to TRS API endpoints, the `TRSClient` class also provides access
methods for additional endpoints implemented in
[TRS-Filer][res-elixir-cloud-trs-filer]:

| Method | Endpoint | Description |
| --- | --- | --- |
| [`.post_tool_class()`][docs-api-post_tool_class] | `POST ​/toolClasses` | Create a tool class |
| [`.put_tool_class()`][docs-api-put_tool_class] | `PUT ​/toolClasses​/{id}` | Create or update a tool class |
| [`.delete_tool_class()`][docs-api-delete_tool_class] | `DELETE ​/toolClasses​/{id}` | Delete a tool class |
| [`.post_tool()`][docs-api-post_tool] | `POST ​/tools` | Add a tool |
| [`.put_tool()`][docs-api-put_tool] | `PUT ​/tools​/{id}` | Add or update a tool |
| [`.delete_tool()`][docs-api-delete_tool] | `DELETE ​/tools​/{id}` | Delete a tool |
| [`.post_version()`][docs-api-post_version] | `POST ​/tools​/{id}​/versions` | Add a tool version |
| [`.put_version()`][docs-api-put_version] | `PUT ​/tools​/{id}​/versions​/{version_id}` | Add or update a tool version |
| [`.delete_version()`][docs-api-delete_version] | `DELETE ​/tools​/{id}​/versions​/{version_id}` | Delete a tool version |
| [`.post_service_info()`][docs-api-post_service_info] | `POST ​/service-info` | Register service info |

### Authorization

Authorization [bearer tokens][res-bearer-token] can be provided either during
client instantiation or when calling an endpoint access method. The bearer
token is sent along as an `Authorization` header with every request sent from
the instantiated client instance.

> **NOTE:** Whenever a token is specified when calling an API endpoint, the
> `token` variable of that particular client instance is overridden. Thus,
> subsequent calls from that client will all carry the new token value, unless
> overridden again.

The following example illustrates this behavior:

```py
from trs_cli import TRSClient

# No token passed during client instantiation
client = TRSClient(uri="https://my-trs.app")
# Value of client.token: None

# Token passed during client instantiation
client_2 = TRSClient(
    uri="https://my-trs.app",
    token="MyT0k3n",
)
# Value of client_2.token: MyT0k3n
```

## API documentation

Automatically built [API documentation][docs-api] is available.

## Installation

You can install `TRS-cli` in one of two ways:

### Via package manager

```bash
pip install trs_cli

# Or for the latest development version:
pip install git+https://github.com/elixir-cloud-aai/TRS-cli.git#egg=trs_cli
```

### Manual installation

```bash
git clone https://github.com/elixir-cloud-aai/TRS-cli.git
cd TRS-cli
python setup.py install
```

## Contributing

This project is a community effort and lives off your contributions, be it in
the form of bug reports, feature requests, discussions, or fixes and other code
changes. Please refer to our organization's [contributing
guidelines][res-elixir-cloud-contributing] if you are interested to contribute.
Please mind the [code of conduct][res-elixir-cloud-coc] for all interactions
with the community.

## Versioning

The project adopts the [semantic versioning][res-semver] scheme for versioning.
Currently the service is in beta stage, so the API may change without further
notice.

## License

This project is covered by the [Apache License 2.0][license-apache] also
[shipped with this repository][license].

## Contact

The project is a collaborative effort under the umbrella of [ELIXIR Cloud &
AAI][res-elixir-cloud]. Follow the link to get in touch with us via chat or
email. Please mention the name of this service for any inquiry, proposal,
question etc.

![logo_banner][]

[badge-build-status]:<https://travis-ci.com/elixir-cloud-aai/TRS-cli.svg?branch=dev>
[badge-coverage]:<https://img.shields.io/coveralls/github/elixir-cloud-aai/TRS-cli>
[badge-docs]: <https://readthedocs.org/projects/trs-cli/badge/?version=latest>
[badge-github-tag]:<https://img.shields.io/github/v/tag/elixir-cloud-aai/TRS-cli?color=C39BD3>
[badge-license]:<https://img.shields.io/badge/license-Apache%202.0-blue.svg>
[badge-pypi]:<https://img.shields.io/pypi/v/trs-cli.svg?style=flat&color=C39BD3>
[badge-url-build-status]:<https://travis-ci.com/elixir-cloud-aai/TRS-cli>
[badge-url-coverage]:<https://coveralls.io/github/elixir-cloud-aai/TRS-cli>
[badge-url-docs]: <https://trs-cli.readthedocs.io/en/latest/?badge=latest>
[badge-url-github-tag]:<https://github.com/elixir-cloud-aai/TRS-cli/releases>
[badge-url-license]:<http://www.apache.org/licenses/LICENSE-2.0>
[badge-url-pypi]:<https://pypi.python.org/pypi/trs-cli>
[docs-api]: <https://trs-cli.readthedocs.io/en/latest/>
[docs-api-delete_tool]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.delete_tool>
[docs-api-delete_tool_class]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.delete_tool_class>
[docs-api-delete_version]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.delete_version>
[docs-api-get_containerfiles]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_containerfiles>
[docs-api-get_descriptor]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_descriptor>
[docs-api-get_descriptor_by_path]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_descriptor_by_path>
[docs-api-get_files]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_files>
[docs-api-get_service_info]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_service_info>
[docs-api-get_tests]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_tests>
[docs-api-get_tool]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_tool>
[docs-api-get_tool_classes]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_tool_classes>
[docs-api-get_tools]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_tools>
[docs-api-get_version]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_version>
[docs-api-get_versions]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.get_versions>
[docs-api-post_service_info]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.post_service_info>
[docs-api-post_tool]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.post_tool>
[docs-api-post_tool_class]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.post_tool_class>
[docs-api-post_version]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.post_version>
[docs-api-put_tool]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.put_tool>
[docs-api-put_tool_class]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.put_tool_class>
[docs-api-put_version]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.put_version>
[docs-api-retrieve_files]: <https://trs-cli.readthedocs.io/en/latest/modules/trs_cli.html#trs_cli.client.TRSClient.retrieve_files>
[license]: LICENSE
[license-apache]: <https://www.apache.org/licenses/LICENSE-2.0>
[logo_banner]: images/logo-banner.png
[res-bearer-token]: <https://tools.ietf.org/html/rfc6750>
[res-elixir-cloud]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai>
[res-elixir-cloud-coc]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CODE_OF_CONDUCT.md>
[res-elixir-cloud-contributing]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CONTRIBUTING.md>
[res-elixir-cloud-trs-filer]: <https://github.com/elixir-cloud-aai/trs-filer>
[res-eosc-workflow-hub]: <https://workflowhub.eu/>
[res-ga4gh]: <https://www.ga4gh.org/>
[res-ga4gh-trs]: <https://github.com/ga4gh/tool-registry-service-schemas>
[res-ga4gh-trs-version]: <https://github.com/ga4gh/tool-registry-service-schemas/blob/91a57cd93caf380019d4952c0c74bb7e343e647b/openapi/openapi.yaml>
[res-ga4gh-trs-uri]: <https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris>
[res-pydantic]: <https://pydantic-docs.helpmanual.io/>
[res-pydantic-docs-export]: <https://pydantic-docs.helpmanual.io/usage/exporting_models/>
[res-semver]: <https://semver.org/>
