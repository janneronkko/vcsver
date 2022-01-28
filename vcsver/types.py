import typing


class RevisionInfo(typing.NamedTuple):  # Pylint issue 3876 pylint: disable=inherit-non-class
    latest_tag: typing.Optional[str]
    distance: typing.Optional[int]
    commit: typing.Optional[str]
    dirty: bool


class VersionInfo(typing.NamedTuple):  # Pylint issue 3876 pylint: disable=inherit-non-class
    latest_release: str
    distance: typing.Optional[int]
    commit: typing.Optional[str]
    dirty: bool


RevisionInfoReader = typing.Callable[[], typing.Optional[RevisionInfo]]

RevisionInfoReaderFactory = typing.Callable[[], RevisionInfoReader]

TagParser = typing.Callable[[str], str]

VersionStringFactory = typing.Callable[[VersionInfo], str]
