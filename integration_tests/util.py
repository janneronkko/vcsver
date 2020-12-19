import subprocess

import vcsver.run
from vcsver.run import CalledProcessError  # pylint: disable=unused-import


def run(*cmd, **kwargs):
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.PIPE)

    return vcsver.run.run(cmd, **kwargs)
