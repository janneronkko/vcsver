import abc
import pathlib
import sys
import typing

from .virtualenv import VirtualEnv
from . import util


class PackagingImplementation(abc.ABC):
    @property
    def supports_build_time_dependencies(self) -> bool:
        return True

    @abc.abstractmethod
    def create_packaging_files(
        self,
        project_dir: pathlib.Path,
        *,
        name: str,
        manual_version: typing.Optional[str] = None,
        vcsver_enabled: bool = True,
    ) -> None:
        pass

    @abc.abstractmethod
    def build(
        self,
        project_dir: pathlib.Path,
    ) -> None:
        pass


class SetuptoolsWithSetupPy(PackagingImplementation):
    @property
    def supports_build_time_dependencies(self) -> bool:
        # setup.py's setup_requires only allows package names, i.e. you can only depend on released versions this way
        return False

    def __init__(
        self,
        vcsver_wheel_path: pathlib.Path,
        venv: VirtualEnv,
    ) -> None:
        super().__init__()

        self._venv = venv

        self._venv.install(
            'wheel',
            str(vcsver_wheel_path),
        )

    def create_packaging_files(
        self,
        project_dir: pathlib.Path,
        *,
        name: str,
        manual_version: typing.Optional[str] = None,
        vcsver_enabled: bool = True,
    ) -> None:
        setup_kwargs: typing.List[typing.Tuple[str, typing.Any]] = []

        if manual_version is not None:
            setup_kwargs.append(('version', manual_version))

        if vcsver_enabled:
            setup_kwargs.append(('vcsver', True))

        util.render_template(
            'setup.py',
            project_dir / 'setup.py',
            context={
                'name': name,
                'setup_kwargs': setup_kwargs,
            },
        )

    def build(
        self,
        project_dir: pathlib.Path,
    ) -> None:
        self._venv.run_python(
            'setup.py',
            'sdist',
            'bdist_wheel',
            check=True,
            cwd=str(project_dir),
        )


class SetuptoolsWithPyprojectToml(PackagingImplementation):
    def __init__(
        self,
        vcsver_wheel_path: pathlib.Path,
    ) -> None:
        super().__init__()

        self.vcsver_wheel_path = vcsver_wheel_path

    def create_packaging_files(
        self,
        project_dir: pathlib.Path,
        *,
        name: str,
        manual_version: typing.Optional[str] = None,
        vcsver_enabled: bool = True,
    ) -> None:
        util.render_template(
            'setup.cfg',
            project_dir / 'setup.cfg',
            context={
                'name': name,
                'version': manual_version,
            },
        )

        util.render_template(
            'pyproject.toml',
            project_dir / 'pyproject.toml',
            context={
                'vcsver_wheel_path': self.vcsver_wheel_path,
                'vcsver_enabled': vcsver_enabled,
            },
        )

    def build(
        self,
        project_dir: pathlib.Path,
    ) -> None:
        util.run(
            sys.executable,
            '-m', 'build',
            check=True,
            cwd=str(project_dir),
        )
