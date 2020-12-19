import pytest

from .. import types
from .. import git


def test_outside_git_clone(fake_process):
    fake_process.register_subprocess(
        ('git', 'rev-parse', '--show-toplevel'),
        stdout=b'',
        returncode=128,
    )

    read_revision_info = git.GitRevisionInfoReader()

    assert read_revision_info() is None


def test_with_no_commits(fake_process):
    fake_process.register_subprocess(
        ('git', 'rev-parse', '--show-toplevel'),
        stdout=b'/git/repo',
    )

    fake_process.register_subprocess(
        ('git', 'describe', '--dirty', '--always', '--long', '--abbrev=10'),
        stdout=b'fatal: bad revision \'HEAD\'',
        returncode=128,
    )

    read_revision_info = git.GitRevisionInfoReader()

    assert read_revision_info() == types.RevisionInfo(
        latest_tag=None,
        distance=0,
        commit=None,
        dirty=True,
    )


@pytest.mark.parametrize(
    ('describe_output', 'commits', 'expected_revision_info'),
    (
        (b'912dd9d', 1, types.RevisionInfo(latest_tag=None, distance=1, commit='912dd9d', dirty=False)),
        (b'912dd9d-dirty', 2, types.RevisionInfo(latest_tag=None, distance=2, commit='912dd9d', dirty=True)),
        (b'1.0-0-g912dd9d', 10, types.RevisionInfo(latest_tag='1.0', distance=0, commit='912dd9d', dirty=False)),
        (b'1.0-1-g912dd9d', 11, types.RevisionInfo(latest_tag='1.0', distance=1, commit='912dd9d', dirty=False)),
        (b'1.0-2-g912dd9d-dirty', 12, types.RevisionInfo(latest_tag='1.0', distance=2, commit='912dd9d', dirty=True)),
    ),
)
def test_with_commits(
    fake_process,
    describe_output,
    commits,
    expected_revision_info,
):
    fake_process.register_subprocess(
        ('git', 'rev-parse', '--show-toplevel'),
        stdout=b'/git/repo',
    )

    fake_process.register_subprocess(
        ('git', 'describe', '--dirty', '--always', '--long', '--abbrev=10'),
        stdout=describe_output,
    )

    fake_process.register_subprocess(
        ('git', 'log', '--oneline'),
        stdout='\n'.join(str(index) for index in range(0, commits)).encode() + b'\n'
    )

    read_revision_info = git.GitRevisionInfoReader()
    assert read_revision_info() == expected_revision_info
