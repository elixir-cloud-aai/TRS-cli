# TRS-cli

[![License][badge-license]][badge-url-license]
[![Build_status][badge-build-status]][badge-url-build-status]
[![Coverage][badge-coverage]][badge-url-coverage]
[![GitHub_tag][badge-github-tag]][badge-url-github-tag]
[![PyPI_release][badge-pypi]][badge-url-pypi]

Client for implementations of the [Global Alliance for Genomics and
Health (GA4GH)][res-ga4gh] [Tool Registry Service API][res-ga4gh-trs] schema,
including support for additional endpoints defined in [ELIXIR Cloud &
AAI's][res-elixir-cloud] generic [TRS-Filer][res-elixir-cloud-trs-filer] TRS
implementation.

## Usage

To use the client import it as follows in your Python code after
[installation](#Installation):

### Create client instance

#### Via TRS hostname

A client instance can be created by specifying the domain name of a TRS
instance, including the URL schema:

```py
from trs_cli.client import TRSClient

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
from trs_cli.client import TRSClient

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
from trs_cli.client import TRSClient

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
from trs_cli.client import TRSClient

client = TRSClient(
    uri="trs://my-trs.app/SOME_TOOL",
    use_http=True,
)
# Client instantiated for URL: http://my-trs.app:443/ga4gh/trs/v1
```

### Access endpoints

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

#### `GET` endpoints

Coming soon...

#### `POST` & `PUT` endpoints

Coming soon...

#### `DELETE` endpoints

Coming soon...

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
from trs_cli.client import TRSClient

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

## API docs

Automatically built [API documentation][docs-api] is available.

## Installation

You can install `TRS-cli` in one of two ways:

### Installation via package manager

```bash
pip install trs_cli

# Or for latest development version:
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
[badge-github-tag]:<https://img.shields.io/github/v/tag/elixir-cloud-aai/TRS-cli?color=C39BD3>
[badge-license]:<https://img.shields.io/badge/license-Apache%202.0-blue.svg>
[badge-pypi]:<https://img.shields.io/pypi/v/trs-cli.svg?style=flat&color=C39BD3>
[badge-url-build-status]:<https://travis-ci.com/elixir-cloud-aai/TRS-cli>
[badge-url-coverage]:<https://coveralls.io/github/elixir-cloud-aai/TRS-cli>
[badge-url-github-tag]:<https://github.com/elixir-cloud-aai/TRS-cli/releases>
[badge-url-license]:<http://www.apache.org/licenses/LICENSE-2.0>
[badge-url-pypi]:<https://pypi.python.org/pypi/trs-cli>
[docs-api]: <https://trs-cli.readthedocs.io/en/latest/>
[license]: LICENSE
[license-apache]: <https://www.apache.org/licenses/LICENSE-2.0>
[logo_banner]: images/logo-banner.png
[res-bearer-token]: <https://tools.ietf.org/html/rfc6750>
[res-elixir-cloud]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai>
[res-elixir-cloud-coc]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CODE_OF_CONDUCT.md>
[res-elixir-cloud-contributing]: <https://github.com/elixir-cloud-aai/elixir-cloud-aai/blob/dev/CONTRIBUTING.md>
[res-elixir-cloud-trs-filer]: <https://github.com/elixir-cloud-aai/trs-filer>
[res-ga4gh]: <https://www.ga4gh.org/>
[res-ga4gh-trs]: <https://github.com/ga4gh/tool-registry-service-schemas>
[res-ga4gh-trs-uri]: <https://ga4gh.github.io/tool-registry-service-schemas/DataModel/#trs_uris>
[res-pydantic]: <https://pydantic-docs.helpmanual.io/>
[res-pydantic-docs-export]: <https://pydantic-docs.helpmanual.io/usage/exporting_models/>
[res-semver]: <https://semver.org/>
