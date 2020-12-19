import subprocess


def run(*cmd, **kwargs):
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.PIPE)

    return subprocess.run(cmd, **kwargs)  # pylint: disable=subprocess-run-check
