import collections.abc

from .vcsver import get_version


def vcsver(dist, attr, value):  # pylint: disable=unused-argument
    get_version_kwargs = dist.vcsver

    if not isinstance(get_version_kwargs, collections.abc.Mapping):
        if not get_version_kwargs:
            return

        get_version_kwargs = {}

    version = get_version(**get_version_kwargs)
    if version is not None:
        dist.metadata.version = version
