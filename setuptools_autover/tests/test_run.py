import subprocess

import pytest

from .. import run


@pytest.mark.parametrize(
    ('returncode', 'check'),
    (
        (0, False),
        (5, False),
        (0, True),
        (5, True),
    ),
)
def test_non_checked_successful_run(
    fake_process,
    returncode,
    check,
):
    fake_process.register_subprocess(
        ('test-command', 'arg1', 'arg2'),
        stdout=b'stdout\n',
        stderr=b'stderr\n',
        returncode=returncode,
    )

    try:
        result = run.run(
            ('test-command', 'arg1', 'arg2'),
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert returncode == 0 or not check
        assert result.returncode == returncode
        assert result.stdout == b'stdout\n'
        assert result.stderr == b'stderr\n'

    except run.CalledProcessError as err:
        assert check
        assert returncode != 0

        assert err.cmd == ('test-command', 'arg1', 'arg2')
        assert err.returncode == returncode
        assert err.stdout == b'stdout\n'
        assert err.stderr == b'stderr\n'
        assert str(err) == 'Command {cmd} returned non-zero returncode ({returncode}):\n{stderr}'.format(
            cmd=('test-command', 'arg1', 'arg2'),
            returncode=returncode,
            stderr='> stderr\n> ',
        )
