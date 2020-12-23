import typing


class RevisionInfo(typing.NamedTuple):  # Pylint issue 3876 pylint: disable=inherit-non-class
    latest_tag: typing.Optional[str]  # Pylint issue 3882 pylint: disable=unsubscriptable-object
    distance: typing.Optional[int]  # Pylint issue 3882 pylint: disable=unsubscriptable-object
    commit: typing.Optional[str]  # Pylint issue 3882 pylint: disable=unsubscriptable-object
    dirty: bool


class VersionInfo(typing.NamedTuple):  # Pylint issue 3876 pylint: disable=inherit-non-class
    latest_release: str
    distance: typing.Optional[int]  # Pylint issue 3882 pylint: disable=unsubscriptable-object
    commit: typing.Optional[str]  # Pylint issue 3882 pylint: disable=unsubscriptable-object
    dirty: bool
