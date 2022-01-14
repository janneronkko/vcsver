import pathlib
import re
import typing

from . import git


class PythonProject:
    _DIST_FILE_TYPES = (
        (re.compile(r'\.whl$'), 'wheel'),
        (re.compile(r'\.tar\.gz$'), 'sdist'),
    )

    def __init__(
        self,
        path: pathlib.Path,
    ) -> None:
        super().__init__()

        self.path = path

    @property
    def dist_dir(self) -> pathlib.Path:
        return self.path / 'dist'

    def get_dist_files(self) -> typing.Dict[str, pathlib.Path]:
        result: typing.Dict[str, pathlib.Path] = {}

        for dist_file in self.dist_dir.iterdir():
            for regexp, dist_file_type in self._DIST_FILE_TYPES:
                if regexp.search(dist_file.name):
                    assert dist_file_type not in result, (
                        dist_file_type,
                        dist_file.name,
                        result[dist_file_type].name,
                    )

                    result[dist_file_type] = dist_file

        return result


class GitPythonProject(PythonProject):
    def __init__(
        self,
        git_clone: git.GitClone,
    ) -> None:
        super().__init__(git_clone.path)

        self.git_clone = git_clone
