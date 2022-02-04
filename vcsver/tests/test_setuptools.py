import pytest

from .. import (
    pep440,
    setuptools,
)


@pytest.mark.parametrize(
    ('config', 'expect_version_set'),
    (
        ({}, False),
        ({'source': None}, False),
        ({'source': 'git'}, True),
    ),
)
def test_finalize_distribution_options(
    mocker,
    config,
    expect_version_set,
):
    mocker.patch(
        'vcsver.config.read',
        return_value=config,
    )

    get_version_mock = mocker.patch(
        'vcsver.vcsver.get_version',
        return_value=mocker.sentinel.version,
    )

    dist_mock = mocker.Mock()
    del dist_mock.metadata.version

    setuptools.finalize_distribution_options(dist_mock)

    if not expect_version_set:
        assert not get_version_mock.called
        assert not hasattr(dist_mock.metadata, 'version')
        return

    get_version_mock.assert_called_once_with(
        root_version='0',
        read_revision_info=mocker.ANY,
        parse_tag=mocker.ANY,
        create_version=pep440.post,
    )

    assert dist_mock.metadata.version == mocker.sentinel.version
