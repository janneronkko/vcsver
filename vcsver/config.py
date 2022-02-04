import typing

import tomli

from . import errors


Config = typing.Dict[str, typing.Any]


def read() -> Config:
    try:
        pyproject_data = _read_pyproject_toml()

    except FileNotFoundError:
        return {}

    config = pyproject_data.get('tool', {}).get('vcsver', {})

    _validate_config(config)

    return config


def _read_pyproject_toml() -> Config:
    with open('pyproject.toml', 'rb') as pyproject_toml_file:
        return tomli.load(pyproject_toml_file)


def _validate_config(config: Config):
    source = config.get('source')
    if source is not None:
        if source != 'git':
            raise errors.InvalidConfigurationError(
                f'Unknown source: {source}',
            )
