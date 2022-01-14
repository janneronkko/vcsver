import contextlib
import pathlib
import tarfile
import tempfile
import typing

from .virtualenv import VirtualEnv
from . import (
    packaging,
    pythonproject,
)


class VersionGenerationTest:
    def __init__(
        self,
        packaging_impl: packaging.PackagingImplementation,
        virtualenv: VirtualEnv,
        get_vcsver_wheel_path: typing.Callable[[], pathlib.Path],
    ) -> None:
        super().__init__()

        self.packaging_impl = packaging_impl
        self.virtualenv = virtualenv
        self.get_vcsver_wheel_path = get_vcsver_wheel_path

    def __call__(
        self,
        project: pythonproject.PythonProject,
        expected_version: str,
        **create_packaging_files_kwargs: typing.Any,
    ) -> None:
        package_name = 'vcsver-test-project'

        self.packaging_impl.create_packaging_files(
            project.path,
            name=package_name,
            **create_packaging_files_kwargs,
        )

        self.packaging_impl.build(project.path)

        for dist_type, dist_file_path in project.get_dist_files().items():
            if dist_type == 'sdist' and self.is_setuptools_without_pyproject_toml(project):
                self.install_setuptools_package_without_pep518_from_sdist(dist_file_path)

            else:
                self.virtualenv.install(str(dist_file_path))

            installed = self.virtualenv.get_installed()
            assert installed[package_name] == expected_version, (dist_type, type(project), project)

            self.virtualenv.uninstall(package_name)

    def is_setuptools_without_pyproject_toml(
        self,
        project: pythonproject.PythonProject,
    ) -> bool:
        if project.path.joinpath('pyproject.toml').is_file():
            return False

        return (
            project.path.joinpath('setup.py').is_file()
            or project.path.joinpath('setup.cfg').is_file()
        )

    def install_setuptools_package_without_pep518_from_sdist(
        self,
        dist_file_path: pathlib.Path,
    ) -> None:
        # Setuptools packaging without PEP 518 build system dependencies can not install sdist tarball
        # directly so that vcsver is able to generate correct version. vcsver does work when the setup.py
        # is invoked directly
        with self.extracted_sdist(dist_file_path) as sdist_dir:
            # vcsver needs to be manually installed as the test project setup.py/.cfg does not contain
            # setup_requires as it can only reference PyPi package name, i.e. setuptools installs the
            # package from PyPi
            self.virtualenv.install(str(self.get_vcsver_wheel_path()))
            self.virtualenv.run_python(
                'setup.py',
                'install',
                cwd=str(sdist_dir),
            )
            self.virtualenv.uninstall('vcsver')

    @contextlib.contextmanager
    def extracted_sdist(
        self,
        sdist_tarbal_path: pathlib.Path,
    ) -> typing.Generator[
        pathlib.Path,
        None,
        None,
    ]:
        sdist_suffix = '.tar.gz'

        assert sdist_tarbal_path.name.endswith(sdist_suffix), sdist_tarbal_path

        with tarfile.open(str(sdist_tarbal_path), 'r') as sdist_tarbal:
            with tempfile.TemporaryDirectory() as temp_dir:
                sdist_tarbal.extractall(temp_dir)

                # .removesuffix is added in Python 3.9, i.e. when support for Python 3.8 is dropped, this can be
                # updated to use .removesuffix
                yield pathlib.Path(temp_dir) / sdist_tarbal_path.name[:-len(sdist_suffix)]
