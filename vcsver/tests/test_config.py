import pytest

import toml

from .. import (
    errors,
    config,
)


@pytest.mark.parametrize(
    ('pyproject_data', 'expected_config',),
    (
        ({}, {}),
        ({'vcsver': {'source': 'something'}}, {}),
        (
            {'tool': {'vcsver': {'future-option': 'future-value'}}},
            {'future-option': 'future-value'},
        ),
        ({'tool': {'vcsver': {'source': 'git'}}}, {'source': 'git'}),
    ),
)
def test_read(
    mocker,
    pyproject_data,
    expected_config,
):
    match = mocker.mock_open(
        read_data=toml.dumps(pyproject_data).encode('utf-8'),
    )
    mocker.patch('vcsver.config.open', match)

    assert config.read() == expected_config

    match.assert_called_once_with('pyproject.toml', 'rb')


def test_pyproject_toml_not_found(
    mocker,
):
    mocker.patch(
        'vcsver.config.open',
        side_effect=FileNotFoundError(),
    )

    assert config.read() == {}


@pytest.mark.parametrize(
    'config_data',
    (
        {'source': 'foo'},
    ),
)
def test_read_invalid_config(
    mocker,
    config_data,
):
    pyproject_data = {
        'tool': {
            'vcsver': config_data,
        },
    }
    match = mocker.mock_open(
        read_data=toml.dumps(pyproject_data).encode('utf-8'),
    )
    mocker.patch('vcsver.config.open', match)

    with pytest.raises(errors.InvalidConfigurationError):
        config.read()
