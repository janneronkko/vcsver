import collections.abc

from . import autover


def use_autover(dist, attr, value):  # pylint: disable=unused-argument
    get_version_kwargs = dist.use_autover

    if not isinstance(get_version_kwargs, collections.abc.Mapping):
        if not get_version_kwargs:
            return

        get_version_kwargs = {}

    version = autover.get_version(**get_version_kwargs)
    if version is not None:
        dist.metadata.version = version
