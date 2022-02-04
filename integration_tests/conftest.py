from __future__ import annotations

import pathlib
import os
import typing

import filelock
import pytest

from .version_generation_test import VersionGenerationTest
from .virtualenv import VirtualEnv
from . import (
    git,
    packaging,
    pythonproject,
    vcsver_wheel_factory,
)


PACKAGING_IMPLEMENTATIONS = {
    'setuptools-with-setup-py': lambda vcsver_wheel_path, tmpdir_factory: packaging.SetuptoolsWithSetupPy(
        vcsver_wheel_path,
        VirtualEnv.create(tmpdir_factory.mktemp('venv-setup.py_only')),
    ),
    'setuptools-with-pyproject-toml': lambda vcsver_wheel_path, tmpdir_factory: packaging.SetuptoolsWithPyprojectToml(
        vcsver_wheel_path,
    ),
}


def pytest_addoption(parser):
    parser.addoption(
        '--vcsver-packaging',
        action='append',
        help='Set packaging implementations to use.',
        choices=list(PACKAGING_IMPLEMENTATIONS),
    )


@pytest.fixture(
    scope='session',
    name='get_vcsver_wheel_path',
)
def _get_vcsver_wheel_path(
    tmpdir_factory,
    worker_id,
):
    get_vcsver_wheel_path = vcsver_wheel_factory.VcsverWheelFactory(tmpdir_factory)
    if worker_id == 'master':
        return get_vcsver_wheel_path

    vcsver_wheel_path_file_path = os.path.normpath(os.path.join(
        tmpdir_factory.getbasetemp(),
        '..',
        'vcsver-wheel',
    ))

    def get() -> pathlib.Path:
        with filelock.FileLock(f'{vcsver_wheel_path_file_path}.lock'):  # pylint: disable=abstract-class-instantiated
            try:
                with open(vcsver_wheel_path_file_path, 'rt', encoding='utf-8') as vcsver_wheel_path_file:
                    return pathlib.Path(vcsver_wheel_path_file.read())

            except FileNotFoundError:
                path = get_vcsver_wheel_path()
                with open(vcsver_wheel_path_file_path, 'wt', encoding='utf-8') as vcsver_wheel_path_file:
                    vcsver_wheel_path_file.write(str(path))

                return path

    return get


@pytest.fixture
def vcs_test_project_without_vcs(
    tmpdir,
    test_project_git_clone,
):
    for filename in (
        'vcsvertest.py',
        'README',
    ):
        with open(tmpdir / filename, 'wt', encoding='utf-8') as dest_file:
            test_project_git_clone.show(
                f'HEAD:{filename}',
                dest_file,
            )

    return pythonproject.PythonProject(pathlib.Path(str(tmpdir)))


@pytest.fixture
def vcs_test_project_with_git_history(
    test_project_git_clone,
):
    test_project_git_clone.clean(
        directories=True,
        ignored=True,
    )
    test_project_git_clone.reset(
        'origin/main',
        mode='hard',
    )

    return pythonproject.GitPythonProject(
        test_project_git_clone,
    )


@pytest.fixture(
    scope='session',
    name='test_project_git_clone',
)
def _test_project_git_clone(tmpdir_factory):
    return git.GitClone.clone(
        'https://github.com/janneronkko/vcsver-test-project.git',
        pathlib.Path(tmpdir_factory.mktemp('vcsver-test-project.git')),
    )


def pytest_generate_tests(metafunc):
    if 'packaging_impl' not in metafunc.fixturenames:
        return

    metafunc.parametrize(
        'packaging_impl',
        metafunc.config.getoption('vcsver_packaging') or list(PACKAGING_IMPLEMENTATIONS),
        indirect=True,
    )


@pytest.fixture(
    scope='session',
    name='packaging_impl',
)
def _packaging_impl(
    request,
    tmpdir_factory,
    get_vcsver_wheel_path,
):
    return PACKAGING_IMPLEMENTATIONS[request.param](
        get_vcsver_wheel_path(),
        tmpdir_factory,
    )


@pytest.fixture(
    scope='session',
    name='virtualenv_directory',
)
def _virtualenv_directory(tmpdir_factory):
    return VirtualEnv.create(tmpdir_factory.mktemp('virtualenv'))


@pytest.fixture(name='virtualenv')
def _virtualenv(virtualenv_directory):
    virtualenv_directory.reset()

    return virtualenv_directory


@pytest.fixture
def version_generation_test(
    packaging_impl: typing.Any,
    virtualenv: VirtualEnv,
    get_vcsver_wheel_path: typing.Callable[[], pathlib.Path],
) -> typing.Callable[
    [pythonproject.PythonProject, str],
    None,
]:
    return VersionGenerationTest(
        packaging_impl,
        virtualenv,
        get_vcsver_wheel_path,
    )
