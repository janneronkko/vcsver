import typing

from . import git
from . import pep440
from . import types


RevisionInfoReader = typing.Callable[[], typing.Optional[types.RevisionInfo]]  # Pylint issue 3882 pylint: disable=unsubscriptable-object,line-too-long
RevisionInfoReaderFactory = typing.Callable[[], RevisionInfoReader]
TagParser = typing.Callable[[str], str]
VersionStringFactory = typing.Callable[[types.VersionInfo], str]

ConfigDict = typing.Dict[str, typing.Any]


REVISION_INFO_READERS: typing.Dict[
    str,
    RevisionInfoReaderFactory,
] = {
    'git': git.GitRevisionInfoReader,
}

TAG_PARSERS: typing.Dict[
    str,
    TagParser,
] = {
    'plain': lambda tag: tag,
}

VERSION_SCHEMAS: typing.Dict[str, VersionStringFactory] = {
    'pep440.post': pep440.post,
    'pep440.post_with_dev': pep440.post_with_dev,
}


DEFAULT_ROOT_VERSION: str = '0'
DEAULT_READ_REVISION_INFO: RevisionInfoReader = REVISION_INFO_READERS['git']()
DEFAULT_PARSE_TAG: TagParser = TAG_PARSERS['plain']
DEFAULT_CREATE_VERSION: VersionStringFactory = VERSION_SCHEMAS['pep440.post']


def get_version_kwargs(config: ConfigDict) -> typing.Dict[str, typing.Any]:
    return {
        'root_version': config.get('root_version', DEFAULT_ROOT_VERSION),
        'read_revision_info': _get_revision_info_reader(config),
        'parse_tag': _get_parse_tag(config),
        'create_version': _get_create_version(config),
    }


def _get_revision_info_reader(config: ConfigDict) -> RevisionInfoReader:
    revision_info_reader = config.get('read_revision_info', DEAULT_READ_REVISION_INFO)
    if isinstance(revision_info_reader, str):
        revision_info_reader = REVISION_INFO_READERS[revision_info_reader]()

    return revision_info_reader


def _get_parse_tag(config: ConfigDict) -> TagParser:
    parse_tag = config.get('parse_tag', DEFAULT_PARSE_TAG)
    if isinstance(parse_tag, str):
        parse_tag = TAG_PARSERS[parse_tag]

    return parse_tag


def _get_create_version(config: ConfigDict) -> VersionStringFactory:
    create_version = config.get('create_version', DEFAULT_CREATE_VERSION)
    if isinstance(create_version, str):
        create_version = VERSION_SCHEMAS[create_version]

    return create_version
