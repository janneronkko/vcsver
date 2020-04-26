import collections.abc
import warnings

from . import errors
from . import git
from . import pep440
from . import types
from . import util


DEFAULT_CONFIG = {
    'root_version': '0',
    'read_revision_info': git.GitRevisionInfoReader(),
    'parse_tag': lambda tag: tag,
    'create_version': pep440.create_post_with_dev,
}


def handle_use_autover(dist, attr, value):  # pylint: disable=unused-argument
    get_version_kwargs = dist.use_autover

    if not isinstance(get_version_kwargs, collections.abc.Mapping):
        if not get_version_kwargs:
            return

        get_version_kwargs = {}

    version = get_version(**get_version_kwargs)
    if version is not None:
        dist.metadata.version = version


def config_to_get_version_kwargs(config):
    warnings.warn(
        'config_to_get_versino_kwargs is deprecated and will be removed in version 2.0',
        category=DeprecationWarning,
    )

    kwargs = {
        key: config.get(key, default_value)
        for key, default_value in DEFAULT_CONFIG.items()
    }

    unknown_items = {
        key: value
        for key, value in config.items()
        if key not in DEFAULT_CONFIG
    }

    if unknown_items:
        raise errors.InvalidConfigError(
            'The configuration contains unknown items.',
            unknown_items,
        )

    return kwargs


def get_version(
    root_version='0',
    read_revision_info=git.GitRevisionInfoReader(),
    parse_tag=lambda tag: tag,
    create_version=pep440.create_post_with_dev,
):
    revision_info = read_revision_info()

    if revision_info is None:
        version_from_pkg_info_file = get_version_from_pkg_info_file()
        if version_from_pkg_info_file is None:
            raise errors.RevisionInfoNotFoundError('No revision info available.')

        return version_from_pkg_info_file

    if revision_info.latest_tag is None:
        latest_release_version = root_version

    else:
        latest_release_version = parse_tag(revision_info.latest_tag)

    version_data = types.VersionInfo(
        latest_release=latest_release_version,
        distance=revision_info.distance,
        commit=revision_info.commit,
        dirty=revision_info.dirty,
    )

    return create_version(version_data)


def get_version_from_pkg_info_file():
    try:
        return util.parse_pkg_info_file('PKG-INFO')['Version']

    except (PermissionError, FileNotFoundError):
        return None
