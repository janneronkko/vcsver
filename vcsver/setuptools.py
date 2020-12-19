import collections.abc

from . import config
from .vcsver import get_version


def vcsver(dist, attr, value):  # pylint: disable=unused-argument
    config_from_setuptools = dist.vcsver

    if not isinstance(config_from_setuptools, collections.abc.Mapping):
        if not config_from_setuptools:
            return

        config_from_setuptools = {}

    get_version_kwargs = config.get_version_kwargs(config_from_setuptools)

    version = get_version(**get_version_kwargs)
    if version is not None:
        dist.metadata.version = version
