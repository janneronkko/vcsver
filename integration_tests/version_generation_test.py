import contextlib
import functools
import pathlib
import tarfile
import tempfile
import typing

from .virtualenv import VirtualEnv
from . import (
    packaging,
    pythonproject,
    util,
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

        util.log_test_state('Creating packaging files')
        self.packaging_impl.create_packaging_files(
            project.path,
            name=package_name,
            **create_packaging_files_kwargs,
        )

        util.log_test_state('Building dist files')
        self.packaging_impl.build(project.path)

        test_install_dist_files = functools.partial(
            self._test_install_dist_files,
            package_name=package_name,
            expected_version=expected_version,
        )

        dist_files = project.get_dist_files()

        test_install_dist_files(dist_files)

        sdist = dist_files.get('sdist')
        if sdist:
            with self.extracted_sdist(sdist) as sdist_project:
                util.log_test_state('Building dist files using sdist')
                self.packaging_impl.build(sdist_project.path)

                test_install_dist_files(sdist_project.get_dist_files())

    def _test_install_dist_files(
        self,
        dist_files: typing.Dict[str, pathlib.Path],
        package_name: str,
        expected_version: str,
    ) -> None:
        for dist_type, dist_file_path in dist_files.items():
            util.log_test_state(f'Testing {dist_type}')
            if dist_type == 'sdist' and not self.packaging_impl.supports_build_time_dependencies:
                self.virtualenv.install(str(self.get_vcsver_wheel_path()))

            self.virtualenv.install(str(dist_file_path))

            installed = self.virtualenv.get_installed()
            assert installed[package_name] == expected_version, (
                f'{installed[package_name]} != {expected_version}',
                dist_file_path.name,
            )

            self.virtualenv.reset()

    @contextlib.contextmanager
    def extracted_sdist(
        self,
        sdist_tarbal_path: pathlib.Path,
    ) -> typing.Generator[
        pythonproject.PythonProject,
        None,
        None,
    ]:
        sdist_suffix = '.tar.gz'

        assert sdist_tarbal_path.name.endswith(sdist_suffix), sdist_tarbal_path

        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(str(sdist_tarbal_path), 'r') as sdist_tarbal:
                sdist_tarbal.extractall(temp_dir)

            # .removesuffix is added in Python 3.9, i.e. when support for Python 3.8 is dropped, this can be
            # updated to use .removesuffix
            yield pythonproject.PythonProject(
                pathlib.Path(temp_dir) / sdist_tarbal_path.name[:-len(sdist_suffix)],
            )
