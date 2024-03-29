# This module contains support for Setuptools via vcsver argument in setup() call in setup.py

import collections.abc
import typing

from . import git
from . import pep440
from . import types
from .vcsver import get_version


ConfigDict = typing.Dict[str, typing.Any]


def vcsver(dist: typing.Any, attr: str, value: typing.Any) -> None:  # pylint: disable=unused-argument
    if not isinstance(value, collections.abc.Mapping):
        if not value:
            return

        value = {}

    version = get_version(**get_version_kwargs(value))
    if version is not None:
        dist.metadata.version = version


def get_version_kwargs(config: ConfigDict) -> typing.Dict[str, typing.Any]:
    return {
        'root_version': config.get('root_version', DEFAULT_ROOT_VERSION),
        'read_revision_info': _get_revision_info_reader(config),
        'parse_tag': _get_parse_tag(config),
        'create_version': _get_create_version(config),
    }


def _get_revision_info_reader(config: ConfigDict) -> types.RevisionInfoReader:
    revision_info_reader = config.get('read_revision_info', DEFAULT_READ_REVISION_INFO)
    if isinstance(revision_info_reader, str):
        revision_info_reader = REVISION_INFO_READERS[revision_info_reader]()

    return revision_info_reader


def _get_parse_tag(config: ConfigDict) -> types.TagParser:
    parse_tag = config.get('parse_tag', DEFAULT_PARSE_TAG)
    if isinstance(parse_tag, str):
        parse_tag = TAG_PARSERS[parse_tag]

    return parse_tag


def _get_create_version(config: ConfigDict) -> types.VersionStringFactory:
    create_version = config.get('create_version', DEFAULT_CREATE_VERSION)
    if isinstance(create_version, str):
        create_version = VERSION_SCHEMAS[create_version]

    return create_version


REVISION_INFO_READERS: typing.Dict[
    str,
    types.RevisionInfoReaderFactory,
] = {
    'git': git.GitRevisionInfoReader,
}

TAG_PARSERS: typing.Dict[
    str,
    types.TagParser,
] = {
    'plain': lambda tag: tag,
}

VERSION_SCHEMAS: typing.Dict[str, types.VersionStringFactory] = {
    'pep440.post': pep440.post,
    'pep440.post_with_dev': pep440.post_with_dev,
}


DEFAULT_ROOT_VERSION: str = '0'
DEFAULT_READ_REVISION_INFO: types.RevisionInfoReader = REVISION_INFO_READERS['git']()
DEFAULT_PARSE_TAG: types.TagParser = TAG_PARSERS['plain']
DEFAULT_CREATE_VERSION: types.VersionStringFactory = VERSION_SCHEMAS['pep440.post']
