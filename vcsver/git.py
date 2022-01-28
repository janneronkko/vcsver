import re
import subprocess
import typing

from . import types


class GitRevisionInfoReader:
    def __init__(
        self,
        path: typing.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._path: typing.Optional[str] = path
        self._abbrev: int = 10

    def __call__(self) -> typing.Optional[types.RevisionInfo]:
        top_level_path = self._get_top_level_path()
        if top_level_path is None:
            return None

        git_describe = self._run_git(
            'describe',
            '--dirty',
            '--always',
            '--long',
            f'--abbrev={self._abbrev}',
        )

        if git_describe.returncode != 0:
            return types.RevisionInfo(
                latest_tag=None,
                distance=0,
                commit=None,
                dirty=True,
            )

        describe_output = git_describe.stdout.strip().decode()

        revision_data = self._parse_describe_output(describe_output)

        if revision_data.latest_tag is None and revision_data.distance is None:
            git_log = self._run_git(
                'log',
                '--oneline',
                check=True,
            )

            distance = len(git_log.stdout.decode().split('\n')) - 1

            revision_data = types.RevisionInfo(
                latest_tag=revision_data.latest_tag,
                distance=distance,
                commit=revision_data.commit,
                dirty=revision_data.dirty,
            )

        return revision_data

    def _parse_describe_output(self, describe_output: str) -> types.RevisionInfo:
        match = re.match(
            r'^'
            r'((?P<tag>.+)-(?P<distance>\d+)-g)?'
            r'(?P<commit_sha>[0-9a-fA-F]+)'
            r'(?P<dirty_flag>-dirty)?'
            r'$',
            describe_output,
        )
        assert match, describe_output

        describe_components = match.groupdict()

        distance: typing.Optional[int] = None

        distance_string = describe_components.get('distance')
        if distance_string is not None:
            distance = int(distance_string)

        dirty = describe_components['dirty_flag'] == '-dirty'

        return types.RevisionInfo(
            latest_tag=describe_components.get('tag'),
            distance=distance,
            commit=describe_components.get('commit_sha'),
            dirty=dirty,
        )

    def _get_top_level_path(self) -> typing.Optional[str]:
        result = self._run_git(
            'rev-parse',
            '--show-toplevel',
        )

        if result.returncode != 0:
            return None

        return result.stdout.decode().strip()

    def _run_git(
        self,
        *args: typing.Any,
        **run_args: typing.Any,
    ) -> subprocess.CompletedProcess:
        run_args.setdefault('stdout', subprocess.PIPE)
        run_args.setdefault('stderr', subprocess.PIPE)

        return subprocess.run(  # pylint: disable=subprocess-run-check
            ('git',) + args,
            cwd=self._path,
            **run_args
        )
