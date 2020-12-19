from . import git
from . import pep440


REVISION_INFO_READERS = {
    'git': git.GitRevisionInfoReader,
}

TAG_PARSERS = {
    'plain': lambda tag: tag,
}

VERSION_SCHEMAS = {
    'pep440.post': pep440.post,
    'pep440.post_with_dev': pep440.post_with_dev,
}


DEFAULT_ROOT_VERSION = '0'
DEAULT_READ_REVISION_INFO = REVISION_INFO_READERS['git']()
DEFAULT_PARSE_TAG = TAG_PARSERS['plain']
DEFAULT_CREATE_VERSION = VERSION_SCHEMAS['pep440.post_with_dev']


def get_version_kwargs(config):
    return {
        'root_version': config.get('root_version', DEFAULT_ROOT_VERSION),
        'read_revision_info': _get_revision_info_reader(config),
        'parse_tag': _get_parse_tag(config),
        'create_version': _get_create_version(config),
    }


def _get_revision_info_reader(config):
    revision_info_reader = config.get('read_revision_info', DEAULT_READ_REVISION_INFO)
    if isinstance(revision_info_reader, str):
        revision_info_reader = REVISION_INFO_READERS[revision_info_reader]()

    return revision_info_reader


def _get_parse_tag(config):
    parse_tag = config.get('parse_tag', DEFAULT_PARSE_TAG)
    if isinstance(parse_tag, str):
        parse_tag = VERSION_SCHEMAS[parse_tag]

    return parse_tag


def _get_create_version(config):
    create_version = config.get('create_version', DEFAULT_CREATE_VERSION)
    if isinstance(create_version, str):
        create_version = VERSION_SCHEMAS[create_version]

    return create_version
