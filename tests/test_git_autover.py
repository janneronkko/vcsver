import os
import subprocess
import unittest

from . import util
from . import tests


class GitTests(tests.AutoverVcsTestsMixin, unittest.TestCase):
    def init_repo(self, repo_dir):
        self._run_git('init', repo_dir)

    def assert_local_part_matches(self, local_part):
        self.assertTrue(self._get_head_sha().startswith(local_part))

    def create_commit(self):
        super().create_commit()

        with open(os.path.join(self.repo_dir, 'dummy.txt'), 'at+') as dummy_file:
            dummy_file.seek(0)
            change_number = len(dummy_file.read().split('\n'))

            dummy_file.write('Dummy change {}\n'.format(change_number))

        self._run_git('add', 'dummy.txt')

        environ = os.environ.copy()
        environ['GIT_AUTHOR_NAME'] = 'Setuptools Autover Test'
        environ['EMAIL'] = 'autover@example.com'

        self._run_git(
            'commit', '-m', 'Dummy change {}'.format(change_number),
            env=environ,
        )

    def create_tag(self, tag_name):
        super().create_tag(tag_name)

        self._run_git('tag', '-a', '-m', 'Version tag', tag_name, 'HEAD')

    def _get_head_sha(self):
        return self._run_git(
            'rev-parse', 'HEAD',
            stdout=subprocess.PIPE,
        ).stdout.decode().strip()

    def _run_git(self, *args, **kwargs):
        kwargs['cwd'] = self.repo_dir
        kwargs['check'] = True

        return util.run('git', *args, **kwargs)
