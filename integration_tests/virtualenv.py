from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from . import util


class VirtualEnv:
    @classmethod
    def create(
        cls,
        path: pathlib.Path,
    ) -> VirtualEnv:
        util.run(
            sys.executable,
            '-m', 'venv',
            str(path),
            check=True,
        )

        return cls(path)

    def __init__(
        self,
        path: pathlib.Path,
    ) -> None:
        super().__init__()

        self.path = path

    @property
    def python(self) -> str:
        return str(self.path / 'bin' / 'python')

    @property
    def pip(self) -> str:
        return str(self.path / 'bin' / 'pip')

    def reset(self) -> None:
        pip_freeze_process = util.run(
            self.pip,
            'freeze',
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )

        if not pip_freeze_process.stdout.strip():
            return

        installed_pkgs_file_path = self.path / 'installed.txt'

        with open(installed_pkgs_file_path, 'wt', encoding='utf-8') as installed_pkgs_file:
            installed_pkgs_file.write(pip_freeze_process.stdout)

        util.run(
            self.pip,
            'uninstall',
            '-r', str(installed_pkgs_file_path),
            check=True,
        )

    def install(self, *requirements):
        if not requirements:
            return

        self.run_pip(
            'install',
            *requirements,
            check=True,
        )

    def uninstall(self, *requirements):
        if not requirements:
            return

        self.run_pip(
            'uninstall',
            '--yes',
            *requirements,
            check=True,
        )

    def get_installed(self):
        pip = self.run_pip(
            'list',
            '--format', 'json',
            check=True,
            stdout=subprocess.PIPE,
        )

        return {
            item['name']: item['version']
            for item in json.loads(pip.stdout)
        }

    def run_pip(self, *args, **kwargs):
        return util.run(
            self.pip,
            '--disable-pip-version-check',
            *args,
            **kwargs)

    def run_python(self, *args, **kwargs):
        return util.run(
            self.python,
            *args,
            **kwargs,
        )
