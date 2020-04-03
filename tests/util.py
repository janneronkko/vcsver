import os
import subprocess
import sys

import setuptools_autover.run
from setuptools_autover.run import CalledProcessError # pylint: disable=unused-import


def run(*cmd, **kwargs):
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.PIPE)

    return setuptools_autover.run.run(cmd, **kwargs)


class Venv:
    def __init__(self, path):
        super().__init__()

        self.path = path

        run(sys.executable, '-m', 'venv', self.path)

    @property
    def python(self):
        return os.path.join(self.path, 'bin', 'python')

    @property
    def pip(self):
        return os.path.join(self.path, 'bin', 'pip')
