#! /usr/bin/env python3

import argparse
import asyncio
import enum
import io
import os
import signal
import sys
import posixpath


SUPPORTED_PYTHON_VERSIONS = {
    '3.5': 'py35',
    '3.6': 'py36',
    '3.7': 'py37',
    '3.8': 'py38',
}


def main():
    args = parse_args()

    loop = asyncio.get_event_loop()

    processes = Processes(live=args.live_log)

    loop.add_signal_handler(signal.SIGINT, processes.terminate)

    run = Runner(processes.run)

    versions = SUPPORTED_PYTHON_VERSIONS
    if args.versions:
        versions = {
            key: value
            for key, value in SUPPORTED_PYTHON_VERSIONS.items()
            if key in args.versions
        }

    loop.run_until_complete(run(versions))


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--live-log',
        help='Print logs from test runs during tests',
        default=False,
        action='store_true',
    )

    parser.add_argument(
        'versions',
        nargs='*',
    )

    return parser.parse_args()


class TerminatedError(Exception):
    def __init__(self, output):
        super().__init__()

        self.output = output


class TestResult:
    class Type(enum.Enum):
        passed = 'passed'
        failed = 'failed'
        aborted = 'aborted'

    def __init__(self, result, python_version, output):
        super().__init__()

        self.result = result
        self.python_version = python_version
        self.output = output

    @property
    def passed(self):
        return self.result == self.Type.passed


class Runner:
    def __init__(self, run_command):
        super().__init__()

        self._run_command = run_command

    async def __call__(self, versions):
        tasks = [
            self._run_tests(python_version, tox_env)
            for python_version, tox_env in versions.items()
        ]

        results = await asyncio.gather(*tasks)

        print()
        for result in results:
            if not result.passed:
                heading = f'Python {result.python_version} failed'
                header_bar = '=' * (((120 - len(heading)) // 2) - 1)
                print(f'{header_bar} {heading} {header_bar}')
                for line in result.output:
                    print(f'> {line}', end='')
                print('=' * 120)
                print()

        print('Summary:')
        for result in results:
            print(f'  Python {result.python_version}: {result.result.value}')

    async def _run_tests(self, python_version, tox_env):
        print(f'Running Tox env {tox_env} on Python {python_version}...')
        try:
            this_dir = os.path.dirname(__file__)
            if not os.path.isabs(this_dir):
                this_dir = os.path.join(os.getcwd(), this_dir)

            docker_image = f'tox:latest-{python_version}'

            returncode, stdout = await self._run_command(
                'docker', 'build',
                '--build-arg', f'PYTHON_VERSION={python_version}',
                '--file', 'Dockerfile.tox',
                '--tag', docker_image,
                this_dir,
                tag=python_version,
            )
            if returncode != 0:
                return TestResult(
                    TestResult.Type.failed,
                    python_version,
                    stdout,
                )

            data_dir = f'/work/.docker-tox/{python_version}'
            stat = os.stat(this_dir)

            returncode, stdout = await self._run_command(
                'docker', 'run',
                '--rm',
                '--volume', f'{this_dir}:/work',
                '--user', f'{stat.st_uid}:{stat.st_gid}',
                '--workdir', '/work',
                '--env', 'HOME={}'.format(posixpath.join(data_dir, 'home')),
                docker_image,
                'tox',
                '--workdir', posixpath.join(data_dir, 'workdir'),
                '-e', tox_env,
                tag=python_version,
            )

            print(f'Tox env {tox_env} on Python {python_version} finished.')
            return TestResult(
                TestResult.Type.passed if returncode == 0 else TestResult.Type.failed,
                python_version,
                stdout,
            )

        except TerminatedError as err:
            return TestResult(
                TestResult.Type.aborted,
                python_version,
                err.output,
            )


class Processes:
    def __init__(self, live):
        super().__init__()

        self._live = live
        self._processes = {}
        self._terminated = False

    def terminate(self):
        self._terminated = True
        for process in self._processes.values():
            process.send_signal(signal.SIGKILL)

    async def run(self, *args, tag, **kwargs):
        command = ' '.join(
            f'"{arg}"' if ' ' in arg else arg
            for arg in args
        )
        self._live_log(tag, command)

        stdout = io.StringIO()

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            **kwargs,
        )

        try:
            self._processes[process.pid] = process

            line = '\n'
            while not process.stdout.at_eof():
                line = await process.stdout.readline()
                line = line.decode()
                stdout.write(line)

                self._live_log(tag, line)

            await process.wait()

            stdout.seek(0)

            if self._terminated:
                raise TerminatedError(stdout)

            return process.returncode, stdout

        finally:
            self._processes.pop(process.pid, None)

    def _live_log(self, tag, line):
        if not self._live:
            return

        line = line.rstrip()
        sys.stdout.write(f'{tag} > {line}\n')


if __name__ == '__main__':
    main()
