import unittest

from .. import types
from .. import git
from . import helpers


class TestReadingVersionInfo(unittest.TestCase, helpers.MockMixin):
    def setUp(self):
        super().setUp()

        self.read_revision_info = git.GitRevisionInfoReader()

        self.patch('setuptools_autover.run.run', side_effect=self._run_mock)
        self._run_results = {}
        self._run_expected_args = {
            ('git', 'describe'): {
                '--dirty',
                '--always',
                '--long',
                '--abbrev=10',
            },

            ('git', 'log'): {
                '--oneline',
            },

            ('git', 'rev-parse'): {
                '--show-toplevel',
            }
        }

        self._set_rev_parse_result('/git/repo')

    def _run_mock(self, cmd, *args, **kwargs): # pylint: disable=unused-argument
        cmd_key = cmd[0:2]

        result = self._run_results.get(cmd_key)
        self.assertIsNotNone(result, cmd)
        self.assertEqual(self._run_expected_args.get(cmd_key), set(cmd[2:]), cmd_key)

        return result

    def _set_rev_parse_result(self, output, returncode=0):
        result = self.mock(name='git rev-parse result')
        result.returncode = returncode
        result.stdout = output.encode()

        self._run_results[('git', 'rev-parse')] = result

    def _set_describe_result(self, output, returncode=0):
        result = self.mock(name='git describe result')
        result.returncode = returncode
        result.stdout = output.encode()

        self._run_results[('git', 'describe')] = result

    def _set_log_result(self, commits, returncode=0):
        result = self.mock(name='git log result')
        result.returncode = returncode
        result.stdout = '\n'.join(str(index) for index in range(0, commits)).encode() + b'\n'

        self._run_results[('git', 'log')] = result

    def test_read_data_when_not_inside_git_repo(self):
        self._set_rev_parse_result('', 128)

        self.assertIsNone(self.read_revision_info())

    def test_read_data_from_repo_not_having_any_commits(self):
        self._set_describe_result('fatal: bad revision \'HEAD\'', 128)

        self.assertEqual(
            self.read_revision_info(),
            types.RevisionInfo(latest_tag=None, distance=0, commit=None, dirty=True),
        )

    def test_read_data_from_repo_not_having_tags(self):
        for describe_output, commits, expected in (
            ('912dd9d', 1, types.RevisionInfo(latest_tag=None, distance=1, commit='912dd9d', dirty=False)),
            ('912dd9d-dirty', 2, types.RevisionInfo(latest_tag=None, distance=2, commit='912dd9d', dirty=True)),
        ):
            with self.subTest(describe=describe_output, commits=commits):
                self._set_describe_result(describe_output)
                self._set_log_result(commits)

                data = self.read_revision_info()

                self.assertEqual(data, expected)

    def test_read_data_from_repo_having_tags(self):
        for describe_output, expected in (
            ('1.0-0-g912dd9d', types.RevisionInfo(latest_tag='1.0', distance=0, commit='912dd9d', dirty=False)),
            ('1.0-1-g912dd9d', types.RevisionInfo(latest_tag='1.0', distance=1, commit='912dd9d', dirty=False)),
            ('1.0-2-g912dd9d-dirty', types.RevisionInfo(latest_tag='1.0', distance=2, commit='912dd9d', dirty=True)),
        ):
            with self.subTest(describe=describe_output):
                self._set_describe_result(describe_output)

                data = self.read_revision_info()

                self.assertEqual(data, expected)
