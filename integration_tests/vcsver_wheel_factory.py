import pathlib
import sys
import typing

from . import util


VCSVER_LOCAL_DIR = (pathlib.Path(__file__) / '..' / '..').resolve()


class VcsverWheelFactory:
    def __init__(
        self,
        tmpdir_factory: typing.Any,
    ) -> None:
        super().__init__()

        self._tmpdir_factory = tmpdir_factory
        self._path: typing.Optional[pathlib.Path] = None

    def __call__(self) -> pathlib.Path:
        if self._path is None:
            dist_dir = pathlib.Path(
                str(self._tmpdir_factory.mktemp('setup_py_virtualenv')),
            )
            util.run(
                sys.executable,
                '-m', 'build',
                '--wheel',
                '--outdir', str(dist_dir),
                str(VCSVER_LOCAL_DIR),
                check=True,
            )

            dist_files = list(dist_dir.iterdir())
            assert len(dist_files) == 1, dist_files

            wheel_file = dist_files[0]
            assert wheel_file.suffix == '.whl', wheel_file

            self._path = wheel_file

        return self._path
