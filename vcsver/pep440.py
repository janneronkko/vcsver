from . import types


def post(version_info: types.VersionInfo) -> str:
    latest_version = version_info.latest_release

    dirty_separator = '+'
    if version_info.distance != 0:
        latest_version = f'{latest_version}.post{version_info.distance}+{version_info.commit}'
        dirty_separator = '.'

    if version_info.dirty:
        latest_version = f'{latest_version}{dirty_separator}dirty'

    return latest_version


def post_with_dev(version_info: types.VersionInfo) -> str:
    latest_version = version_info.latest_release

    dirty_separator = '+'
    if version_info.distance != 0:
        latest_version = f'{latest_version}.post0.dev{version_info.distance}+{version_info.commit}'
        dirty_separator = '.'

    if version_info.dirty:
        latest_version = f'{latest_version}{dirty_separator}dirty'

    return latest_version
