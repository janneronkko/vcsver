import pytest

from .. import config
from .. import setuptools


@pytest.mark.parametrize(
    ('vcsver', 'expected_version'),
    (
        (None, None),
        (True, '1.2.3'),
        ({}, '1.2.3'),
        ({'root_version': '1.0'}, '1.2.3'),
    ),
)
def test_vcsver(
    mocker,
    vcsver,
    expected_version,
):
    get_version_mock = mocker.patch(
        'vcsver.setuptools.get_version',
        return_value='1.2.3',
    )

    dist_mock = mocker.Mock(name='Dist')
    dist_mock.vcsver = vcsver
    dist_mock.metadata.version = None

    setuptools.vcsver(
        dist_mock,
        mocker.sentinel.attr,
        mocker.sentinel.value,
    )

    assert dist_mock.metadata.version == expected_version

    if vcsver is None:
        assert not get_version_mock.called
        return

    if isinstance(vcsver, dict):
        expected_get_version_call_kwargs = config.get_version_kwargs(vcsver)

    else:
        expected_get_version_call_kwargs = config.get_version_kwargs({})

    get_version_mock.assert_called_once_with(**expected_get_version_call_kwargs)
