from packaging.version import (
    parse as parse_version,
    Version,
)
import pytest

from .. import pep440
from ..types import VersionInfo


@pytest.mark.parametrize(
    ('version_info', 'expected_version_string'),
    (
        (VersionInfo(latest_release='1.0', distance=0, commit='abcdef', dirty=False), '1.0'),
        (VersionInfo(latest_release='1.0', distance=0, commit='abcdef', dirty=True), '1.0+dirty'),
        (VersionInfo(latest_release='1.0', distance=1, commit='abcdef', dirty=False), '1.0.post0.dev1+abcdef'),
        (VersionInfo(latest_release='1.0', distance=1, commit='abcdef', dirty=True), '1.0.post0.dev1+abcdef.dirty'),
    ),
)
def test_pep440_post_with_dev(version_info, expected_version_string):
    assert pep440.post_with_dev(version_info) == expected_version_string


_PEP440_POST_WITH_DEV_VERSIONS = (
    '1.0',
    '1.0.post0.dev1',
    '1.1.dev0',
    '1.1',
    '1.1+dirty',
    '1.1.post0.dev1+abcdef.dirty',
)


def _version_order_cases(version_strings):
    return list(zip(
        version_strings,
        version_strings[1:],
    ))


@pytest.mark.parametrize(
    ('prev_version', 'next_version'),
    _version_order_cases(_PEP440_POST_WITH_DEV_VERSIONS),
)
def test_version_ordering(prev_version, next_version):
    prev_version = parse_version(prev_version)
    assert isinstance(prev_version, Version)

    next_version = parse_version(next_version)
    assert isinstance(next_version, Version)

    # Make sure that the version strings generated match the ordering used by packaging library
    assert prev_version < next_version
