import functools
import pathlib
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

        test_install_dist_files = functools.partial(
            self._test_install_dist_files,
            package_name=package_name,
            expected_version=expected_version,
        )

        dist_files = project.get_dist_files()

        test_install_dist_files(dist_files)

    def _test_install_dist_files(
        self,
        dist_files: typing.Dict[str, pathlib.Path],
        package_name: str,
        expected_version: str,
    ) -> None:
        for dist_type, dist_file_path in dist_files.items():
            if dist_type == 'sdist' and not self.packaging_impl.supports_build_time_dependencies:
                self.virtualenv.install(str(self.get_vcsver_wheel_path()))

            self.virtualenv.install(str(dist_file_path))

            installed = self.virtualenv.get_installed()
            assert installed[package_name] == expected_version, (
                f'{installed[package_name]} != {expected_version}',
                dist_file_path.name,
            )

            self.virtualenv.reset()
