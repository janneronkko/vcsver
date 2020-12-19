import subprocess


class CalledProcessError(Exception):
    def __init__(self, cmd, stdout, stderr, returncode):
        super().__init__()

        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __str__(self):
        return 'Command {cmd} returned non-zero returncode ({returncode}):\n{stderr}'.format(
            cmd=self.cmd,
            returncode=self.returncode,
            stderr='\n'.join('> {}'.format(line.rstrip()) for line in self.stderr.decode().split('\n')),
        )


def run(cmd, *args, check=False, **kwargs):
    process = subprocess.Popen(cmd, *args, **kwargs)

    stdout, stderr = process.communicate()

    if check and process.returncode != 0:
        raise CalledProcessError(
            cmd,
            stdout,
            stderr,
            process.returncode,
        )

    process.stdout = stdout
    process.stderr = stderr

    return process
