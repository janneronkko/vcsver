import subprocess

import setuptools_autover.run
from setuptools_autover.run import CalledProcessError  # pylint: disable=unused-import


def run(*cmd, **kwargs):
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.PIPE)

    return setuptools_autover.run.run(cmd, **kwargs)
