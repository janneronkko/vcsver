import os
import shutil
import subprocess
import tempfile
import unittest

import pkg_resources

from . import util


TEMPLATE_DIR = os.path.dirname(__file__)
AUTOVER_ROOT_DIR = os.path.dirname(TEMPLATE_DIR)


class AutoverTestsMixin(object):
    PKG_NAME = 'testpkg'

    @classmethod
    def setUpClass(cls): # pylint: disable=invalid-name
        cls.venv_temp_dir = tempfile.TemporaryDirectory()

        try:
            cls.venv = util.Venv(cls.venv_temp_dir.name)

            util.run(
                cls.venv.python, 'setup.py', 'install',
                check=True,
                cwd=AUTOVER_ROOT_DIR,
            )

        except:
            cls.venv_temp_dir.cleanup()
            raise

    @classmethod
    def tearDownClass(cls): # pylint: disable=invalid-name
        super().tearDownClass()

        cls.venv_temp_dir.cleanup()

    def setUp(self): # pylint: disable=invalid-name
        super().setUp()

        self.repo_temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.repo_temp_dir.cleanup)

        self.repo_dir = self.repo_temp_dir.name

        self.init_repo(self.repo_dir)

        self._init_test_pkg(self.repo_temp_dir.name)

    def init_repo(self, repo_dir):
        pass

    def read_setup_py_version(self):
        version_str = util.run(
            self.venv.python, 'setup.py', '--version',
            stdout=subprocess.PIPE,
            check=True,
            cwd=self.repo_dir,
        ).stdout.decode()

        return pkg_resources.parse_version(version_str)

    def _init_test_pkg(self, target_dir):
        for file_name in ('setup.py', 'testpkg.py'):
            with open(os.path.join(TEMPLATE_DIR, '{}.tmpl'.format(file_name)), 'rt') as tmpl_file:
                tmpl = tmpl_file.read()

            contents = tmpl.format(
                name=self.PKG_NAME,
            )

            with open(os.path.join(target_dir, file_name), 'wt') as target_file:
                target_file.write(contents)


class AutoverVcsTestsMixin(AutoverTestsMixin):
    ROOT_VERSION = '0'

    def setUp(self):
        super().setUp()

        self.version_of_latest_tag = self.ROOT_VERSION
        self.commits_since_latest_tag = 0

    def create_commit(self):
        self.commits_since_latest_tag += 1

    def create_tag(self, tag_name):
        self.commits_since_latest_tag = 0
        self.version_of_latest_tag = tag_name

    def test_initial_commit_without_tags(self):
        self.create_commit()

        self._test_versions()

    def test_initial_commit_with_tag(self):
        self.create_commit()
        self.create_tag('0.1')

        self._test_versions()

    def test_multiple_commits_without_tags(self):
        self.create_commit()
        self.create_commit()
        self.create_commit()

        self._test_versions()

    def test_multiple_commits_with_latest_commit_tagged(self):
        self.create_commit()
        self.create_commit()
        self.create_tag('1.0')

        self._test_versions()

    def test_multiple_commits_after_latest_tag(self):
        self.create_commit()
        self.create_commit()
        self.create_commit()
        self.create_tag('1.0')
        self.create_commit()
        self.create_commit()
        self.create_commit()
        self.create_commit()

        self._test_versions()

    def _test_versions(self):
        setup_py_version = self._test_setup_py_version()

        with self.subTest('sdist'):
            self._test_sdist(setup_py_version)

        with self.subTest('wheel'):
            self._test_wheel(setup_py_version)

    def _test_setup_py_version(self):
        setup_py_version = self.read_setup_py_version()

        self.assertEqual(setup_py_version.base_version, self.version_of_latest_tag)

        if self.commits_since_latest_tag == 0:
            expected_public_version = self.version_of_latest_tag

        else:
            expected_public_version = '{}.post0.dev{}'.format(
                self.version_of_latest_tag,
                self.commits_since_latest_tag,
            )

        self.assertIsInstance(setup_py_version, pkg_resources.SetuptoolsVersion)

        self.assertEqual(setup_py_version.public, expected_public_version)

        if setup_py_version.local is not None:
            self.assert_local_part_matches(setup_py_version.local)

        return setup_py_version

    def _test_sdist(self, expected_version):
        self._test_install(expected_version, 'sdist', install_requires_autover=True)

    def _test_wheel(self, expected_version):
        util.run(
            self.venv.pip, 'install', 'wheel',
            check=True,
        )

        self._test_install(expected_version, 'bdist_wheel')

    def _test_install(self, expected_version, dist, *, install_requires_autover=False):
        dist_dir = os.path.join(self.repo_dir, 'dist')
        shutil.rmtree(dist_dir, ignore_errors=True)

        util.run(
            self.venv.python, 'setup.py', dist,
            check=True,
            cwd=self.repo_dir,
        )
        dist_files = os.listdir(dist_dir)

        self.assertEqual(len(dist_files), 1)

        package_path = os.path.join(self.repo_dir, 'dist', dist_files[0])

        with tempfile.TemporaryDirectory() as temp_dir:
            venv = util.Venv(temp_dir)

            if install_requires_autover:
                util.run(
                    venv.python, 'setup.py', 'install',
                    check=True,
                    cwd=AUTOVER_ROOT_DIR,
                )

            util.run(
                venv.pip, 'install', package_path,
                check=True,
                cwd=temp_dir,
            )

            util.run(
                venv.pip, 'list',
                check=True,
                cwd=temp_dir,
            )

            installed_version = util.run(
                venv.python,
                '-c',
                'import pkg_resources; print(pkg_resources.get_distribution("{}").version)'.format(self.PKG_NAME),
                stdout=subprocess.PIPE,
                check=True,
                cwd=temp_dir,
            ).stdout.decode().strip()
            installed_version = pkg_resources.parse_version(installed_version)

            self.assertEqual(installed_version, expected_version)


class NoVcsTest(AutoverTestsMixin, unittest.TestCase):
    def test_read_version_from_setup_py(self):
        with self.assertRaises(util.CalledProcessError) as context:
            self.read_setup_py_version()

        stderr = context.exception.stderr.decode()
        self.assertIn(
            'setuptools_autover.errors.RevisionInfoNotFoundError:',
            stderr.strip().split('\n')[-1],
        )
