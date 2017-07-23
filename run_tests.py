#! /usr/bin/env python3

import asyncio
import os
import signal


SUPPORTED_PYTHON_VERSIONS = (
    '3.4',
    '3.5',
    '3.6',
)


def main():
    loop = asyncio.get_event_loop()

    run = Runner()

    loop.add_signal_handler(signal.SIGINT, run.terminate)

    loop.run_until_complete(run())


class Runner(object):
    def __init__(self):
        super().__init__()

        self._terminating = False
        self._processes = {}

    def terminate(self):
        self._terminating = True
        for process in self._processes.values():
            process.send_signal(signal.SIGKILL)

    async def __call__(self):
        tasks = [
            self._run_tests(python_version)
            for python_version in SUPPORTED_PYTHON_VERSIONS
        ]

        results = await asyncio.gather(*tasks)

        if not self._terminating:
            for python_version, passed, stdout in results:
                print('Python {}: {}'.format(python_version, 'pass' if passed else 'fail'))
                if not passed:
                    for line in stdout.split('\n'):
                        print(f'> {line}')

    async def _run_tests(self, python_version):
        print(f'Running tests with Python {python_version}')

        this_dir = os.path.dirname(__file__)
        if not os.path.isabs(this_dir):
            this_dir = os.path.join(os.getcwd(), this_dir)

        process = await asyncio.create_subprocess_exec(
            'docker', 'run',
            '--rm',
            '-v', f'{this_dir}:/autover',
            f'python:{python_version}-alpine',
            'sh', '-c', _TEST_SCRIPT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        self._processes[process.pid] = process

        stdout, stderr = await process.communicate() # pylint: disable=unused-variable

        del self._processes[process.pid]

        if not self._terminating:
            print(f'Tests on Python {python_version} done')

        return (
            python_version,
            process.returncode == 0,
            stdout.decode(),
        )


_TEST_SCRIPT = '''
set -e

apk add --update git
cd /autover
adduser -D -u $(stat -c %g setup.py) user
su user -c "python -m unittest discover -v"
'''

if __name__ == '__main__':
    main()
