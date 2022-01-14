import abc
import pathlib
import typing

from .virtualenv import VirtualEnv
from . import util


class PackagingImplementation(abc.ABC):
    @abc.abstractmethod
    def create_packaging_files(
        self,
        project_dir: pathlib.Path,
        *,
        name: str,
        manual_version: typing.Optional[str] = None,
        vcsver: typing.Optional[bool] = None,
    ) -> None:
        pass

    @abc.abstractmethod
    def build(
        self,
        project_dir: pathlib.Path,
    ) -> None:
        pass


class SetuptoolsSetupPy(PackagingImplementation):
    def __init__(
        self,
        venv: VirtualEnv,
    ) -> None:
        super().__init__()

        self._venv = venv

    def create_packaging_files(
        self,
        project_dir: pathlib.Path,
        *,
        name: str,
        manual_version: typing.Optional[str] = None,
        vcsver: typing.Optional[bool] = None,
    ) -> None:
        setup_kwargs: typing.List[typing.Tuple[str, typing.Any]] = []

        if manual_version is not None:
            setup_kwargs.append(('version', manual_version))

        if vcsver is not None:
            setup_kwargs.append(('vcsver', vcsver))

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
