import subprocess

import pytest


def test_manually_defined_version_vcsver_disabled(
    vcs_test_project_without_vcs,
    version_generation_test,
):
    version_generation_test(
        vcs_test_project_without_vcs,
        '1.2.3',
        manual_version='1.2.3',
        vcsver_enabled=False,
    )


@pytest.mark.parametrize(
    'manual_version',
    (
        None,
        '1.2.3',
    ),
)
def test_get_version_from_vcs(
    vcs_test_project_without_vcs,
    packaging_impl,
    manual_version,
):
    packaging_impl.create_packaging_files(
        vcs_test_project_without_vcs.path,
        name='vcsver-test-project',
        manual_version=manual_version,
        vcsver_enabled=True,
    )

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        packaging_impl.build(vcs_test_project_without_vcs.path)

    assert 'vcsver.errors.RevisionInfoNotFoundError: No revision info available.' in excinfo.value.stdout
