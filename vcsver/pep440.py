def create_post_with_dev(version_info):
    latest_version = version_info.latest_release

    dirty_separator = '+'
    if version_info.distance != 0:
        latest_version = '{tag_version}.post0.dev{distance}+{commit}'.format(
            tag_version=latest_version,
            distance=version_info.distance,
            commit=version_info.commit,
        )
        dirty_separator = '.'

    if version_info.dirty:
        latest_version = '{}{}dirty'.format(latest_version, dirty_separator)

    return latest_version
