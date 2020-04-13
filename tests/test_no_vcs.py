import pytest

from . import util


def test_get_version(test_project):
    with pytest.raises(util.CalledProcessError) as excinfo:
        test_project.get_current_version_from_project_dir()

    stderr = excinfo.value.stderr.decode()
    assert 'setuptools_autover.errors.RevisionInfoNotFoundError:' in stderr.strip().split('\n')[-1]
