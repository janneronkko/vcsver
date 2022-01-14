import collections.abc
import typing

from . import config
from .vcsver import get_version


def vcsver(dist: typing.Any, attr: str, value: typing.Any) -> None:  # pylint: disable=unused-argument
    if not isinstance(value, collections.abc.Mapping):
        if not value:
            return

        value = {}

    get_version_kwargs = config.get_version_kwargs(value)

    version = get_version(**get_version_kwargs)
    if version is not None:
        dist.metadata.version = version
