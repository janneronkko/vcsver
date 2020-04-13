import os
import subprocess

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
        environ['GIT_AUTHOR_NAME'] = 'Setuptools Autover Test'
        environ['GIT_AUTHOR_EMAIL'] = 'autover@example.com'
        environ['GIT_COMMITTER_NAME'] = 'Setuptools Autover Test'
        environ['GIT_COMMITTER_EMAIL'] = 'autover@example.com'
        kwargs['env'] = environ

        return util.run('git', *args, **kwargs)


def test_initial_history_without_tags(test_project):
    vcs = Git(test_project.path)

    test_project.assert_current_version('{}+dirty'.format(test_project.root_version))

    vcs.create_commit()
    test_project.assert_current_version(
        '{}.post0.dev1+{}'.format(
            test_project.root_version,
            vcs.get_local_version_string(),
        ),
    )

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        '{}.post0.dev3+{}'.format(
            test_project.root_version,
            vcs.get_local_version_string(),
        ),
    )


def test_history_with_tags(test_project):
    vcs = Git(test_project.path)

    vcs.create_commit()
    vcs.create_commit()

    vcs.create_tag('1.0')
    test_project.assert_current_version('1.0')

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        '1.0.post0.dev2+{}'.format(
            vcs.get_local_version_string(),
        ),
    )

    vcs.create_commit()
    vcs.create_commit()
    test_project.assert_current_version(
        '1.0.post0.dev4+{}'.format(
            vcs.get_local_version_string(),
        ),
    )
