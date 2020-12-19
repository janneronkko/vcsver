import subprocess

import pytest


def test_get_version_from_vcs(test_project):
    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        test_project.get_current_version_from_project_dir()

    stderr = excinfo.value.stderr.decode()
    assert 'vcsver.errors.RevisionInfoNotFoundError:' in stderr.strip().split('\n')[-1]


def test_get_version_defined_in_setup_py(test_project):
    test_project.set_setup_kwargs(version='1.2.3')

    test_project.assert_current_version('1.2.3')
