import typing

from . import errors
from . import config
from . import types
from . import util


def get_version(
    root_version: str,
    read_revision_info: config.RevisionInfoReader,
    parse_tag: config.TagParser,
    create_version: config.VersionStringFactory,
) -> str:
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


def get_version_from_pkg_info_file() -> typing.Optional[str]:  # Pylint issue 3882 pylint: disable=unsubscriptable-object,line-too-long
    try:
        return util.parse_pkg_info_file('PKG-INFO')['Version']

    except (PermissionError, FileNotFoundError):
        return None
