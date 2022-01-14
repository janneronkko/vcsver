import subprocess

import pytest


def test_manually_defined_version(
    vcs_test_project_without_vcs,
    version_generation_test,
):
    version_generation_test(
        vcs_test_project_without_vcs,
        '1.2.3',
        manual_version='1.2.3',
    )


def test_get_version_from_vcs(
    vcs_test_project_without_vcs,
    packaging_impl,
):
    packaging_impl.create_packaging_files(
        vcs_test_project_without_vcs.path,
        name='vcsver-test-project',
        vcsver=True,
    )

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        packaging_impl.build(vcs_test_project_without_vcs.path)

    assert 'vcsver.errors.RevisionInfoNotFoundError: No revision info available.' in excinfo.value.stdout
