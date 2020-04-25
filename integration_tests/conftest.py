import itertools
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile

import mako.template
import packaging
import pytest

from . import util

TEMPLATE_DIR = os.path.dirname(__file__)
AUTOVER_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope='session')
def virtualenv():
    with tempfile.TemporaryDirectory() as temp_dir:
        venv = VirtualEnv(temp_dir)

        venv.run_python(
            'setup.py', 'develop',
            check=True,
            cwd=AUTOVER_ROOT_DIR,
        )

        yield venv


class VirtualEnv:
    def __init__(self, path):
        super().__init__()

        self.path = path

        util.run(sys.executable, '-m', 'venv', self.path)
        self.install_packages(
            'coverage',
            'wheel',
        )

    @property
    def coverange(self):
        return os.path.join(self.path, 'bin', 'coverange')

    @property
    def python(self):
        return os.path.join(self.path, 'bin', 'python')

    @property
    def pip(self):
        return os.path.join(self.path, 'bin', 'pip')

    def run_python(self, *args, **kwargs):
        return util.run(self.python, *args, **kwargs)

    def run_python_with_coverage(self, *args, **kwargs):
        env = kwargs.pop('env', None)
        if not env:
            env = os.environ.copy()

        env['COVERAGE_FILE'] = os.path.join(
            os.getcwd(),
            '.coverage.integration-tests',
        )

        # Run through coverage binary so that coverage from integration tests
        # are included. pytest-cov combines all .coverage.* files at the end
        # of test run, i.e. nothing else is required for the coverage from
        # the command below to be included in the final coverage data file.
        return util.run(
            os.path.join(self.path, 'bin', 'coverage'),
            'run',
            '--append',
            '--source', os.path.join(os.getcwd(), 'setuptools_autover'),
            '--rcfile', os.path.join(os.getcwd(), '.coveragerc'),
            *args,
            env=env,
            **kwargs,
        )

    def run_pip(self, *args, **kwargs):
        return util.run(self.pip, *args, **kwargs)

    def install_packages(self, *names):
        if not names:
            return

        self.run_pip(
            '--disable-pip-version-check',
            'install',
            *names,
            cwd=self.path,
            check=True,
        )

    def uninstall_packages(self, *names):
        if not names:
            return

        self.run_pip(
            '--disable-pip-version-check',
            'uninstall',
            '--yes',
            *names,
            cwd=self.path,
            check=True,
        )

    def get_installed_packages(self):
        pip_list = self.run_pip(
            '--isolated',
            '--disable-pip-version-check',
            'list',
            '--format',
            'json',
            cwd=self.path,
            check=True,
            stdout=subprocess.PIPE,
        )

        return json.loads(pip_list.stdout.decode())

    def get_package_data(self, pkg_name):
        pip_show = self.run_pip(
            '--disable-pip-version-check',
            'show',
            pkg_name,
            cwd=self.path,
            check=True,
            stdout=subprocess.PIPE,
        )

        value_re = re.compile(
            r'^'
            r'(?P<key>[-a-zA-Z]+)'
            r':\s*'
            r'(?P<value>([^\s].*)?[^\s])'
            r'$'
        )
        return {
            m.group('key'): m.group('value')
            for m in (
                value_re.match(line)
                for line in pip_show.stdout.decode().split('\n')
            )
            if m
        }


@pytest.fixture()
def test_project(tmpdir, virtualenv):  # pylint: disable=redefined-outer-name
    tmpdir = str(tmpdir)

    project_dir = os.path.join(tmpdir, 'project')
    os.mkdir(project_dir)

    sandbox_dir = os.path.join(tmpdir, 'sandbox')
    os.mkdir(sandbox_dir)

    return TestProject(
        virtualenv,
        project_dir,
        'testpkg',
        sandbox_dir,
    )


class TestProject:
    def __init__(self, virtualenv, path, name, sandbox_dir):  # pylint: disable=redefined-outer-name
        super().__init__()

        self.root_version = '0'
        self.virtualenv = virtualenv
        self.path = path
        self.name = name
        self.setup_kwargs = {
            'use_autover': True,
        }

        self._write_setup_py()
        self._write_template(
            'testpkg.py',
            context={
                'name': self.name,
            },
        )

        self._dist_seqnum = itertools.count(0)
        self._sandbox = VirtualEnv(sandbox_dir)
        self._sandbox.run_python(
            'setup.py', 'develop',
            check=True,
            cwd=AUTOVER_ROOT_DIR,
        )

        self._configuring = False

    def set_setup_kwargs(self, **kwargs):
        self.setup_kwargs = kwargs

        self._write_setup_py()

    def _write_setup_py(self):
        self._write_template(
            'setup.py',
            context={
                'name': self.name,
                'setup_kwargs': self.setup_kwargs.items(),
            },
        )

    def _write_template(self, file_name, context):
        template = mako.template.Template(
            filename=os.path.join(TEMPLATE_DIR, '{}.tmpl'.format(file_name)),
        )

        contents = template.render(
            **context,
        )

        with open(os.path.join(self.path, file_name), 'wt') as target_file:
            target_file.write(contents)

    def assert_current_version(self, expected_version):
        # Make sure the expected version conforms to pep440
        version = packaging.version.parse(expected_version)
        assert isinstance(
            version,
            packaging.version.Version,
        ), type(version)

        assert expected_version == self.get_current_version_from_project_dir()
        assert expected_version == self.get_current_version_from_sdist()
        assert expected_version == self.get_current_version_after_installing_pkg('sdist')
        assert expected_version == self.get_current_version_after_installing_pkg('bdist_wheel')

    def get_current_version_from_project_dir(self):
        return self._get_version_from_project_dir(self.path)

    def get_current_version_from_sdist(self):
        dist_file_path = self.create_dist('sdist')

        with tempfile.TemporaryDirectory() as temp_dir:
            with tarfile.open(dist_file_path, 'r:*') as tar:
                common_path = os.path.commonpath(tar.getnames())
                assert common_path
                assert not any(
                    member.name != common_path and os.path.relpath(member.name, common_path).startswith('.')
                    for member in tar.getmembers()
                )

                tar.extractall(temp_dir)

            sdist_dir = os.path.join(temp_dir, common_path)

            return self._get_version_from_project_dir(sdist_dir)

    def get_current_version_after_installing_pkg(self, dist_name):
        dist_file_path = self.create_dist(dist_name)

        return self._get_version_after_installing(dist_file_path)

    def _get_version_from_project_dir(self, path):
        version_str = self.virtualenv.run_python_with_coverage(
            'setup.py', '--version',
            stdout=subprocess.PIPE,
            check=True,
            cwd=path,
        ).stdout.decode().strip()

        assert not os.path.isdir(
            os.path.join(path, '.eggs'),
        ), 'setuptools_autover or its dependencies were downloaded'

        return version_str

    def _get_version_after_installing(self, pkg_path):
        original_package_names = {
            pkg['name']
            for pkg in self._sandbox.get_installed_packages()
        }

        try:
            self._sandbox.install_packages(pkg_path)

            pkg_info = self._sandbox.get_package_data(self.name)

            return pkg_info['Version']

        finally:
            packages_to_remove = {
                pkg['name']
                for pkg in self._sandbox.get_installed_packages()
                if pkg['name'] not in original_package_names
            }
            self._sandbox.uninstall_packages(*packages_to_remove)

    def create_dist(self, dist_name):
        dist_dir = os.path.join(
            self.path,
            'dist',
            '{:0>4}'.format(next(self._dist_seqnum)),
        )

        self.virtualenv.run_python_with_coverage(
            'setup.py', dist_name, '--dist-dir', dist_dir,
            check=True,
            cwd=self.path,
        )

        dist_files = os.listdir(dist_dir)
        assert len(dist_files) == 1, dist_files

        return os.path.join(
            dist_dir,
            dist_files[0],
        )
