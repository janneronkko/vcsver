from __future__ import annotations

import os
import pathlib
import typing

from . import util


class GitClone:
    @classmethod
    def clone(
        cls,
        url: str,
        path: pathlib.Path,
    ) -> GitClone:
        env = os.environ.copy()
        env['GIT_TERMINAL_PROMPT'] = '0'

        util.run(
            'git',
            'clone',
            url,
            str(path),
            check=True,
            env=env,
        )

        return cls(path)

    def __init__(
        self,
        path: pathlib.Path,
    ) -> None:
        super().__init__()

        self.path = path

        self.env = os.environ.copy()
        self.env['GIT_AUTHOR_NAME'] = 'Setuptools Vcsver Test'
        self.env['GIT_AUTHOR_EMAIL'] = 'vcsver@example.com'
        self.env['GIT_COMMITTER_NAME'] = 'Setuptools Vcsver Test'
        self.env['GIT_COMMITTER_EMAIL'] = 'vcsver@example.com'
        self.env['GIT_TERMINAL_PROMPT'] = '0'

    def show(
        self,
        git_object_ref: str,
        output: typing.TextIO,
    ) -> None:
        self.run_git(
            'show',
            git_object_ref,
            stdout=output,
        )

    def reset(
        self,
        commit_ish: str,
        *,
        mode: typing.Optional[str] = None,
    ) -> None:
        args = [
            option
            for included, option in (
                (mode is not None, f'--{mode}'),
            )
            if included
        ]

        self.run_git(
            'reset',
            *args,
            commit_ish,
        )

    def clean(
        self,
        directories: bool = False,
        ignored: bool = False,
    ) -> None:
        args = [
            option
            for included, option in (
                (directories, '-d'),
                (ignored, '-x'),
            )
            if included
        ]

        self.run_git(
            'clean',
            '-f',
            *args,
        )

    def run_git(self, *args, **kwargs):
        return util.run(
            'git',
            *args,
            check=True,
            cwd=str(self.path),
            env=self.env,
            **kwargs,
        )
