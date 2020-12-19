import os
import subprocess

import pytest

from . import util


class Git:
    def __init__(self, repo_dir):
        super().__init__()

        self.repo_dir = repo_dir

        self._run_git('init', self.repo_dir)

        # If GPG sign is enabled, committing fails because there is no
        # GPG keys for the used test email addresses.
        self._run_git('config', 'commit.gpgsign', 'false')

    def get_local_version_string(self):
        return self._get_head_sha()[:10]

    def create_commit(self):
        with open(os.path.join(self.repo_dir, 'dummy.txt'), 'at+') as dummy_file:
            dummy_file.seek(0)
            change_number = len(dummy_file.read().split('\n'))

            dummy_file.write('Dummy change {}\n'.format(change_number))

        self._run_git('add', 'dummy.txt')

        self._run_git('commit', '-m', 'Dummy change {}'.format(change_number))

    def create_tag(self, tag_name):
        self._run_git(
            'tag',
            '-a',
            '-m', 'Tag {}'.format(tag_name),
            tag_name,
            'HEAD',
        )

    def _get_head_sha(self):
        return self._run_git(
            'rev-parse', 'HEAD',
            stdout=subprocess.PIPE,
        ).stdout.decode().strip()

    def _run_git(self, *args, **kwargs):
        kwargs['cwd'] = self.repo_dir
        kwargs['check'] = True

        environ = kwargs.get('env') or os.environ.copy()
        environ['GIT_AUTHOR_NAME'] = 'Setuptools Vcsver Test'
        environ['GIT_AUTHOR_EMAIL'] = 'vcsver@example.com'
        environ['GIT_COMMITTER_NAME'] = 'Setuptools Vcsver Test'
        environ['GIT_COMMITTER_EMAIL'] = 'vcsver@example.com'
        kwargs['env'] = environ

        return util.run('git', *args, **kwargs)


def test_get_version_defined_in_setup_py(test_project):
    test_project.set_setup_kwargs(version='2.0')

    test_project.assert_current_version('2.0')

    vcs = Git(test_project.path)

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version('2.0')

    vcs.create_tag('1.0')
    test_project.assert_current_version('2.0')

    test_project.set_setup_kwargs(version='2.1')
    test_project.assert_current_version('2.1')


@pytest.mark.parametrize(
    ('setuptools_kwargs', 'dev_version_format_string'),
    (
        (None, '{tag}.post{dist}+{hash}'),
        ({'vcsver': {'create_version': 'pep440.post'}}, '{tag}.post{dist}+{hash}'),
        ({'vcsver': {'create_version': 'pep440.post_with_dev'}}, '{tag}.post0.dev{dist}+{hash}'),
    ),
)
def test_get_version_from_history(
    test_project,
    setuptools_kwargs,
    dev_version_format_string,
):
    if setuptools_kwargs:
        test_project.set_setup_kwargs(**setuptools_kwargs)

    vcs = Git(test_project.path)

    test_project.assert_current_version('{}+dirty'.format(test_project.root_version))

    vcs.create_commit()
    test_project.assert_current_version(
        dev_version_format_string.format(
            tag=test_project.root_version,
            dist=1,
            hash=vcs.get_local_version_string(),
        ),
    )

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        dev_version_format_string.format(
            tag=test_project.root_version,
            dist=3,
            hash=vcs.get_local_version_string(),
        ),
    )

    vcs.create_tag('1.0')
    test_project.assert_current_version('1.0')

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        dev_version_format_string.format(
            tag='1.0',
            dist=2,
            hash=vcs.get_local_version_string(),
        ),
    )

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        dev_version_format_string.format(
            tag='1.0',
            dist=4,
            hash=vcs.get_local_version_string(),
        ),
    )


def test_configuration_having_version_defined_in_setup_py_and_vcsver_enabled(test_project):
    vcs = Git(test_project.path)

    test_project.set_setup_kwargs(version='5.0', vcsver=True)

    vcs.create_commit()
    vcs.create_tag('6.0')

    test_project.assert_current_version('6.0')
