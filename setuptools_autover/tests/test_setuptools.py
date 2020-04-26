import collections

import pytest

from .. import setuptools


@pytest.mark.parametrize(
    ('use_autover', 'expected_version'),
    (
        (None, None),
        (True, '1.2.3'),
        ({}, '1.2.3'),
        ({'root_version': '1.0'}, '1.2.3'),
    ),
)
def test_use_autover(
    mocker,
    use_autover,
    expected_version,
):
    get_version_mock = mocker.patch(
        'setuptools_autover.autover.get_version',
        return_value='1.2.3',
    )

    dist_mock = mocker.Mock(name='Dist')
    dist_mock.use_autover = use_autover
    dist_mock.metadata.version = None

    setuptools.use_autover(
        dist_mock,
        mocker.sentinel.attr,
        mocker.sentinel.value,
    )

    assert dist_mock.metadata.version == expected_version

    if use_autover is None:
        assert not get_version_mock.called
        return

    if isinstance(use_autover, dict):
        expected_get_version_call_kwargs = collections.ChainMap(
            use_autover,
        )

    else:
        expected_get_version_call_kwargs = {}

    get_version_mock.assert_called_once_with(**expected_get_version_call_kwargs)
