import pytest


@pytest.mark.parametrize(
    (
        'commit',
        'expected_version',
    ),
    [
        pytest.param(
            '82fa80e3d79f4f49790b206161d1958ef76ea923',
            '0.post1+82fa80e3d7',
            id='root-commit',
        ),
        pytest.param(
            '1.0',
            '1.0',
            id='commit-with-annotated-tag',
        ),
        pytest.param(
            '3a80aeb398161479982cde6a965b383f452f6ada',
            '1.1.post2+3a80aeb398',
            id='no-explicit-version',
        ),
    ],
)
def test_version_from_git_history(
    vcs_test_project_with_git_history,
    version_generation_test,
    commit,
    expected_version,
):
    vcs_test_project_with_git_history.git_clone.reset(commit, mode='hard')

    version_generation_test(
        vcs_test_project_with_git_history,
        expected_version,
        vcsver_enabled=True,
    )


def test_version_from_git_history_with_explicitly_set_version(
    vcs_test_project_with_git_history,
    version_generation_test,
):
    vcs_test_project_with_git_history.git_clone.reset('8ab771d8aa', mode='hard')

    version_generation_test(
        vcs_test_project_with_git_history,
        '1.0.1',
        vcsver_enabled=True,
        manual_version='2.0',
    )


@pytest.mark.parametrize(
    'commit',
    [
        pytest.param('82fa80e3d79f4f49790b206161d1958ef76ea923', id='root-commit'),
        pytest.param('1.0', id='commit-with-annotated-tag'),
        'origin/main',
    ],
)
def test_manually_defined_version(
    vcs_test_project_with_git_history,
    version_generation_test,
    commit,
):
    vcs_test_project_with_git_history.git_clone.reset(commit, mode='hard')

    version_generation_test(
        vcs_test_project_with_git_history,
        '1.2.3',
        manual_version='1.2.3',
    )
