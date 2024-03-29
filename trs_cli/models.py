# generated by datamodel-codegen:
#   filename:  openapi3.yaml
#   timestamp: 2020-09-24T15:57:54+00:00

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field


class CustomBaseModel(BaseModel):
    """Settings subclass."""

    class Config:
        """Configuration for `pydantic` model class."""
        extra = 'forbid'
        arbitrary_types_allowed = False


class Checksum(CustomBaseModel):
    checksum: str = Field(
        ..., description='The hex-string encoded checksum for the data. '
    )
    type: str = Field(
        ...,
        description='The digest method used to create the checksum.\nThe value (e.g. `sha-256`) SHOULD be listed as `Hash Name String` in the https://github.com/ga4gh-discovery/ga4gh-checksum/blob/master/hash-alg.csv[GA4GH Checksum Hash Algorithm Registry].\nOther values MAY be used, as long as implementors are aware of the issues discussed in https://tools.ietf.org/html/rfc6920#section-9.4[RFC6920].\nGA4GH may provide more explicit guidance for use of non-IANA-registered algorithms in the future.',
    )


class ChecksumRegister(CustomBaseModel):
    checksum: str = Field(
        ..., description='The hex-string encoded checksum for the data. '
    )
    type: str = Field(
        ...,
        description='The digest method used to create the checksum.\nThe value (e.g. `sha-256`) SHOULD be listed as `Hash Name String` in the https://github.com/ga4gh-discovery/ga4gh-checksum/blob/master/hash-alg.csv[GA4GH Checksum Hash Algorithm Registry].\nOther values MAY be used, as long as implementors are aware of the issues discussed in https://tools.ietf.org/html/rfc6920#section-9.4[RFC6920].\nGA4GH may provide more explicit guidance for use of non-IANA-registered algorithms in the future.',
    )


class DescriptorType(str, Enum):
    CWL = 'CWL'
    WDL = 'WDL'
    NFL = 'NFL'
    GALAXY = 'GALAXY'
    SMK = 'SMK'


class Error(CustomBaseModel):
    code: int
    message: Optional[str] = 'Internal Server Error'


class FileWrapper(CustomBaseModel):
    checksum: Optional[List[Checksum]] = Field(
        None,
        description='A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes. ',
        example=[
            {'checksum': 'ea2a5db69bd20a42976838790bc29294df3af02b', 'type': 'sha1'}
        ],
    )
    content: Optional[str] = Field(
        None,
        description='The content of the file itself. One of url or content is required.',
    )
    url: Optional[str] = Field(
        None,
        description='Optional url to the underlying content, should include version information, and can include a git hash.  Note that this URL should resolve to the raw unwrapped content that would otherwise be available in content. One of url or content is required.',
    )


class FileWrapperRegister(CustomBaseModel):
    checksum: Optional[List[ChecksumRegister]] = Field(
        None,
        description='A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes. ',
        example=[
            {'checksum': 'ea2a5db69bd20a42976838790bc29294df3af02b', 'type': 'sha1'}
        ],
    )
    content: Optional[str] = Field(
        None,
        description='The content of the file itself. One of url or content is required.',
    )
    url: Optional[str] = Field(
        None,
        description='Optional url to the underlying content, should include version information, and can include a git hash.  Note that this URL should resolve to the raw unwrapped content that would otherwise be available in content. One of url or content is required.',
    )


class ImageType(str, Enum):
    Docker = 'Docker'
    Singularity = 'Singularity'
    Conda = 'Conda'


class OtherType(Enum):
    JSON = 'JSON'
    OTHER = 'OTHER'


class Organization(CustomBaseModel):
    name: str = Field(
        ...,
        description='Name of the organization responsible for the service',
        example='My organization',
    )
    url: AnyUrl = Field(
        ...,
        description='URL of the website of the organization (RFC 3986 format)',
        example='https://example.com',
    )


class Organization1(CustomBaseModel):
    name: str = Field(
        ...,
        description='Name of the organization responsible for the service',
        example='My organization',
    )
    url: AnyUrl = Field(
        ...,
        description='URL of the website of the organization (RFC 3986 format)',
        example='https://example.com',
    )


class ServiceType(CustomBaseModel):
    artifact: str = Field(
        ...,
        description='Name of the API or GA4GH specification implemented. Official GA4GH types should be assigned as part of standards approval process. Custom artifacts are supported.',
        example='beacon',
    )
    group: str = Field(
        ...,
        description="Namespace in reverse domain name format. Use `org.ga4gh` for implementations compliant with official GA4GH specifications. For services with custom APIs not standardized by GA4GH, or implementations diverging from official GA4GH specifications, use a different namespace (e.g. your organization's reverse domain name).",
        example='org.ga4gh',
    )
    version: str = Field(
        ...,
        description='Version of the API or specification. GA4GH specifications use semantic versioning.',
        example='1.0.0',
    )


class ServiceTypeRegister(CustomBaseModel):
    artifact: str = Field(
        ...,
        description='Name of the API or GA4GH specification implemented. Official GA4GH types should be assigned as part of standards approval process. Custom artifacts are supported.',
        example='beacon',
    )
    group: str = Field(
        ...,
        description="Namespace in reverse domain name format. Use `org.ga4gh` for implementations compliant with official GA4GH specifications. For services with custom APIs not standardized by GA4GH, or implementations diverging from official GA4GH specifications, use a different namespace (e.g. your organization's reverse domain name).",
        example='org.ga4gh',
    )
    version: str = Field(
        ...,
        description='Version of the API or specification. GA4GH specifications use semantic versioning.',
        example='1.0.0',
    )


class ToolClass(CustomBaseModel):
    description: Optional[str] = Field(
        None,
        description='A longer explanation of what this class is and what it can accomplish.',
    )
    id: Optional[str] = Field(None, description='The unique identifier for the class.')
    name: Optional[str] = Field(
        None, description='A short friendly name for the class.'
    )


class ToolClassRegister(CustomBaseModel):
    description: Optional[str] = Field(
        None,
        description='A longer explanation of what this class is and what it can accomplish.',
    )
    name: Optional[str] = Field(
        None, description='A short friendly name for the class.'
    )


class ToolClassRegisterId(CustomBaseModel):
    description: Optional[str] = Field(
        None,
        description='A longer explanation of what this class is and what it can accomplish.',
    )
    id: Optional[str] = Field(None, description='The unique identifier for the class.')
    name: Optional[str] = Field(
        None, description='A short friendly name for the class.'
    )


class FileType(Enum):
    TEST_FILE = 'TEST_FILE'
    PRIMARY_DESCRIPTOR = 'PRIMARY_DESCRIPTOR'
    SECONDARY_DESCRIPTOR = 'SECONDARY_DESCRIPTOR'
    CONTAINERFILE = 'CONTAINERFILE'
    OTHER = 'OTHER'


class ToolFile(CustomBaseModel):
    file_type: Optional[FileType] = None
    path: Optional[str] = Field(
        None,
        description="Relative path of the file.  A descriptor's path can be used with the GA4GH .../{type}/descriptor/{relative_path} endpoint.",
    )


class FileType1(Enum):
    TEST_FILE = 'TEST_FILE'
    PRIMARY_DESCRIPTOR = 'PRIMARY_DESCRIPTOR'
    SECONDARY_DESCRIPTOR = 'SECONDARY_DESCRIPTOR'
    CONTAINERFILE = 'CONTAINERFILE'
    OTHER = 'OTHER'


class ToolFileRegister(CustomBaseModel):
    file_type: Optional[FileType1] = None
    path: Optional[str] = Field(
        None,
        description="Relative path of the file.  A descriptor's path can be used with the GA4GH .../{type}/descriptor/{relative_path} endpoint.",
    )


class TypeRegister(CustomBaseModel):
    __root__: str


class FilesRegister(CustomBaseModel):
    file_wrapper: Optional[FileWrapperRegister] = None
    tool_file: Optional[ToolFileRegister] = None
    type: Optional[TypeRegister] = None


class ImageData(CustomBaseModel):
    checksum: Optional[List[Checksum]] = Field(
        None,
        description='A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes.  This exposes the hashcode for specific image versions to verify that the container version pulled is actually the version that was indexed by the registry.',
        example=[
            {
                'checksum': '77af4d6b9913e693e8d0b4b294fa62ade6054e6b2f1ffb617ac955dd63fb0182',
                'type': 'sha256',
            }
        ],
    )
    image_name: Optional[str] = Field(
        None,
        description='Used in conjunction with a registry_url if provided to locate images.',
    )
    image_type: Optional[ImageType] = None
    registry_host: Optional[str] = Field(
        None,
        description='A docker registry or a URL to a Singularity registry. Used along with image_name to locate a specific image.',
    )
    size: Optional[int] = Field(None, description='Size of the container in bytes.')
    updated: Optional[str] = Field(
        None, description='Last time the container was updated.'
    )


class ImageDataRegister(CustomBaseModel):
    checksum: Optional[List[ChecksumRegister]] = Field(
        None,
        description='A production (immutable) tool version is required to have a hashcode. Not required otherwise, but might be useful to detect changes.  This exposes the hashcode for specific image versions to verify that the container version pulled is actually the version that was indexed by the registry.',
        example=[
            {
                'checksum': '77af4d6b9913e693e8d0b4b294fa62ade6054e6b2f1ffb617ac955dd63fb0182',
                'type': 'sha256',
            }
        ],
    )
    image_name: Optional[str] = Field(
        None,
        description='Used in conjunction with a registry_url if provided to locate images.',
    )
    image_type: Optional[ImageType] = None
    registry_host: Optional[str] = Field(
        None,
        description='A docker registry or a URL to a Singularity registry. Used along with image_name to locate a specific image.',
    )
    size: Optional[int] = Field(None, description='Size of the container in bytes.')
    updated: Optional[str] = Field(
        None, description='Last time the container was updated.'
    )


class Service(CustomBaseModel):
    contactUrl: Optional[AnyUrl] = Field(
        None,
        description='URL of the contact for the provider of this service, e.g. a link to a contact form (RFC 3986 format), or an email (RFC 2368 format).',
        example='mailto:support@example.com',
    )
    createdAt: Optional[datetime] = Field(
        None,
        description='Timestamp describing when the service was first deployed and available (RFC 3339 format)',
        example='2019-06-04T12:58:19Z',
    )
    description: Optional[str] = Field(
        None,
        description='Description of the service. Should be human readable and provide information about the service.',
        example='This service provides...',
    )
    documentationUrl: Optional[AnyUrl] = Field(
        None,
        description='URL of the documentation of this service (RFC 3986 format). This should help someone learn how to use your service, including any specifics required to access data, e.g. authentication.',
        example='https://docs.myservice.example.com',
    )
    environment: Optional[str] = Field(
        None,
        description='Environment the service is running in. Use this to distinguish between production, development and testing/staging deployments. Suggested values are prod, test, dev, staging. However this is advised and not enforced.',
        example='test',
    )
    id: str = Field(
        ...,
        description='Unique ID of this service. Reverse domain name notation is recommended, though not required. The identifier should attempt to be globally unique so it can be used in downstream aggregator services e.g. Service Registry.',
        example='org.ga4gh.myservice',
    )
    name: str = Field(
        ...,
        description='Name of this service. Should be human readable.',
        example='My project',
    )
    organization: Organization = Field(
        ..., description='Organization providing the service'
    )
    type: ServiceType
    updatedAt: Optional[datetime] = Field(
        None,
        description='Timestamp describing when the service was last updated (RFC 3339 format)',
        example='2019-06-04T12:58:19Z',
    )
    version: str = Field(
        ...,
        description='Version of the service being described. Semantic versioning is recommended, but other identifiers, such as dates or commit hashes, are also allowed. The version should be changed whenever the service is updated.',
        example='1.0.0',
    )


class ServiceRegister(CustomBaseModel):
    contactUrl: Optional[AnyUrl] = Field(
        None,
        description='URL of the contact for the provider of this service, e.g. a link to a contact form (RFC 3986 format), or an email (RFC 2368 format).',
        example='mailto:support@example.com',
    )
    createdAt: Optional[datetime] = Field(
        None,
        description='Timestamp describing when the service was first deployed and available (RFC 3339 format)',
        example='2019-06-04T12:58:19Z',
    )
    description: Optional[str] = Field(
        None,
        description='Description of the service. Should be human readable and provide information about the service.',
        example='This service provides...',
    )
    documentationUrl: Optional[AnyUrl] = Field(
        None,
        description='URL of the documentation of this service (RFC 3986 format). This should help someone learn how to use your service, including any specifics required to access data, e.g. authentication.',
        example='https://docs.myservice.example.com',
    )
    environment: Optional[str] = Field(
        None,
        description='Environment the service is running in. Use this to distinguish between production, development and testing/staging deployments. Suggested values are prod, test, dev, staging. However this is advised and not enforced.',
        example='test',
    )
    id: str = Field(
        ...,
        description='Unique ID of this service. Reverse domain name notation is recommended, though not required. The identifier should attempt to be globally unique so it can be used in downstream aggregator services e.g. Service Registry.',
        example='org.ga4gh.myservice',
    )
    name: str = Field(
        ...,
        description='Name of this service. Should be human readable.',
        example='My project',
    )
    organization: Organization1 = Field(
        ..., description='Organization providing the service'
    )
    type: ServiceTypeRegister
    updatedAt: Optional[datetime] = Field(
        None,
        description='Timestamp describing when the service was last updated (RFC 3339 format)',
        example='2019-06-04T12:58:19Z',
    )
    version: str = Field(
        ...,
        description='Version of the service being described. Semantic versioning is recommended, but other identifiers, such as dates or commit hashes, are also allowed. The version should be changed whenever the service is updated.',
        example='1.0.0',
    )


class ToolVersion(CustomBaseModel):
    author: Optional[List[str]] = Field(
        None,
        description='Contact information for the author of this version of the tool in the registry. (More complex authorship information is handled by the descriptor).',
    )
    containerfile: Optional[bool] = Field(
        None,
        description='Reports if this tool has a containerfile available. (For Docker-based tools, this would indicate the presence of a Dockerfile)',
    )
    descriptor_type: Optional[List[DescriptorType]] = Field(
        None, description='The type (or types) of descriptors available.'
    )
    id: str = Field(
        ...,
        description='An identifier of the version of this tool for this particular tool registry.',
        example='v1',
    )
    images: Optional[List[ImageData]] = Field(
        None,
        description='All known docker images (and versions/hashes) used by this tool. If the tool has to evaluate any of the docker images strings at runtime, those ones cannot be reported here.',
    )
    included_apps: Optional[List[str]] = Field(
        None,
        description='An array of IDs for the applications that are stored inside this tool.',
        example=[
            'https://bio.tools/tool/mytum.de/SNAP2/1',
            'https://bio.tools/bioexcel_seqqc',
        ],
    )
    is_production: Optional[bool] = Field(
        None,
        description='This version of a tool is guaranteed to not change over time (for example, a  tool built from a tag in git as opposed to a branch). A production quality tool  is required to have a checksum',
    )
    meta_version: Optional[str] = Field(
        None,
        description='The version of this tool version in the registry. Iterates when fields like the description, author, etc. are updated.',
    )
    name: Optional[str] = Field(None, description='The name of the version.')
    signed: Optional[bool] = Field(
        None, description='Reports whether this version of the tool has been signed.'
    )
    url: str = Field(
        ...,
        description='The URL for this tool version in this registry.',
        example='http://agora.broadinstitute.org/tools/123456/versions/1',
    )
    verified: Optional[bool] = Field(
        None,
        description='Reports whether this tool has been verified by a specific organization or individual.',
    )
    verified_source: Optional[List[str]] = Field(
        None,
        description='Source of metadata that can support a verified tool, such as an email or URL.',
    )


class ToolVersionRegister(CustomBaseModel):
    author: Optional[List[str]] = Field(
        None,
        description='Contact information for the author of this version of the tool in the registry. (More complex authorship information is handled by the descriptor).',
    )
    descriptor_type: Optional[List[DescriptorType]] = Field(
        None, description='The type (or types) of descriptors available.'
    )
    files: Optional[List[FilesRegister]] = Field(
        None,
        description='Properties and (pointers to) contents of files associated with a tool.',
    )
    images: Optional[List[ImageDataRegister]] = Field(
        None,
        description='All known docker images (and versions/hashes) used by this tool. If the tool has to evaluate any of the docker images strings at runtime, those ones cannot be reported here.',
    )
    included_apps: Optional[List[str]] = Field(
        None,
        description='An array of IDs for the applications that are stored inside this tool.',
        example=[
            'https://bio.tools/tool/mytum.de/SNAP2/1',
            'https://bio.tools/bioexcel_seqqc',
        ],
    )
    is_production: Optional[bool] = Field(
        None,
        description='This version of a tool is guaranteed to not change over time (for example, a  tool built from a tag in git as opposed to a branch). A production quality tool  is required to have a checksum.',
    )
    name: Optional[str] = Field(None, description='The name of the version.')
    signed: Optional[bool] = Field(
        None, description='Reports whether this version of the tool has been signed.'
    )
    verified: Optional[bool] = Field(
        None,
        description='Reports whether this tool has been verified by a specific organization or individual.',
    )
    verified_source: Optional[List[str]] = Field(
        None,
        description='Source of metadata that can support a verified tool, such as an email or URL.',
    )


class ToolVersionRegisterId(CustomBaseModel):
    author: Optional[List[str]] = Field(
        None,
        description='Contact information for the author of this version of the tool in the registry. (More complex authorship information is handled by the descriptor).',
    )
    descriptor_type: Optional[List[DescriptorType]] = Field(
        None, description='The type (or types) of descriptors available.'
    )
    files: Optional[List[FilesRegister]] = Field(
        None,
        description='Properties and (pointers to) contents of files associated with a tool.',
    )
    id: str = Field(
        ...,
        description='A unique identifier of the version of this tool for this particular tool registry. If not provided, will be auto-generated by the implementation. Note that a `BadRequest` will be returned if multiple versions with the same `id` properties are provided.',
        example='v1',
    )
    images: Optional[List[ImageDataRegister]] = Field(
        None,
        description='All known docker images (and versions/hashes) used by this tool. If the tool has to evaluate any of the docker images strings at runtime, those ones cannot be reported here.',
    )
    included_apps: Optional[List[str]] = Field(
        None,
        description='An array of IDs for the applications that are stored inside this tool.',
        example=[
            'https://bio.tools/tool/mytum.de/SNAP2/1',
            'https://bio.tools/bioexcel_seqqc',
        ],
    )
    is_production: Optional[bool] = Field(
        None,
        description='This version of a tool is guaranteed to not change over time (for example, a  tool built from a tag in git as opposed to a branch). A production quality tool  is required to have a checksum.',
    )
    name: Optional[str] = Field(None, description='The name of the version.')
    signed: Optional[bool] = Field(
        None, description='Reports whether this version of the tool has been signed.'
    )
    verified: Optional[bool] = Field(
        None,
        description='Reports whether this tool has been verified by a specific organization or individual.',
    )
    verified_source: Optional[List[str]] = Field(
        None,
        description='Source of metadata that can support a verified tool, such as an email or URL.',
    )


class Tool(CustomBaseModel):
    aliases: Optional[List[str]] = Field(
        None,
        description='Support for this parameter is optional for tool registries that support aliases.\nA list of strings that can be used to identify this tool which could be  straight up URLs. \nThis can be used to expose alternative ids (such as GUIDs) for a tool\nfor registries. Can be used to match tools across registries.',
    )
    checker_url: Optional[str] = Field(
        None,
        description='Optional url to the checker tool that will exit successfully if this tool produced the expected result given test data.',
    )
    description: Optional[str] = Field(None, description='The description of the tool.')
    has_checker: Optional[bool] = Field(
        None, description='Whether this tool has a checker tool associated with it.'
    )
    id: str = Field(
        ...,
        description='A unique identifier of the tool, scoped to this registry.',
        example=123456,
    )
    meta_version: Optional[str] = Field(
        None,
        description='The version of this tool in the registry. Iterates when fields like the description, author, etc. are updated.',
    )
    name: Optional[str] = Field(None, description='The name of the tool.')
    organization: str = Field(
        ..., description='The organization that published the image.'
    )
    toolclass: ToolClass
    url: str = Field(
        ...,
        description='The URL for this tool in this registry.',
        example='http://agora.broadinstitute.org/tools/123456',
    )
    versions: List[ToolVersion] = Field(
        ..., description='A list of versions for this tool.'
    )


class ToolRegister(CustomBaseModel):
    aliases: Optional[List[str]] = Field(
        None,
        description='Support for this parameter is optional for tool registries that support aliases. A list of strings that can be used to identify this tool which could be straight up URLs. This can be used to expose alternative ids (such as GUIDs) for a tool for registries. Can be used to match tools across registries.',
        example=[
            '630d31c3-381e-488d-b639-ce5d047a0142',
            'dockstore.org:630d31c3-381e-488d-b639-ce5d047a0142',
            'bio.tools:630d31c3-381e-488d-b639-ce5d047a0142',
        ],
    )
    checker_url: Optional[str] = Field(
        None,
        description='Optional url to the checker tool that will exit successfully if this tool produced the expected result given test data.',
    )
    description: Optional[str] = Field(None, description='The description of the tool.')
    has_checker: Optional[bool] = Field(
        None, description='Whether this tool has a checker tool associated with it.'
    )
    name: Optional[str] = Field(None, description='The name of the tool.')
    organization: str = Field(
        ..., description='The organization that published the image.'
    )
    toolclass: ToolClassRegisterId
    versions: List[Union[ToolVersionRegister, ToolVersionRegisterId]] = Field(
        ..., description='A list of versions for this tool.'
    )
