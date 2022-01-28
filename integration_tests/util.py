import pathlib
import os
import subprocess
import sys
import typing

import colors
import mako.template


TEMPLATE_DIR = (pathlib.Path(__file__) / '..' / 'templates').resolve()


def run(*cmd, **kwargs):
    stdout = kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault(
        'stderr',
        (
            subprocess.STDOUT
            if stdout == subprocess.PIPE
            else subprocess.PIPE
        ),
    )

    kwargs.setdefault('text', True)

    log_commandline(
        kwargs.get('cwd', os.getcwd()),
        cmd,
    )

    try:
        process = subprocess.run(cmd, **kwargs)  # pylint: disable=subprocess-run-check

        _log_process_output(process.stdout, process.stderr)

    except subprocess.CalledProcessError as err:
        _log_process_output(err.output, err.stderr)

        raise

    return process


def _log_process_output(stdout, stderr):
    output = stderr or stdout

    if not output:
        return

    for line in output.split('\n'):
        log_output(line.rstrip())


def render_template(
    template_name: str,
    dest: pathlib.Path,
    context: typing.Dict[str, typing.Any],
) -> None:
    template = mako.template.Template(
        filename=str(TEMPLATE_DIR / f'{template_name}.mako'),
    )

    contents = template.render(**context)

    log_heading(dest.name)
    for line in contents.split('\n'):
        log_output(line.rstrip())

    with open(dest, 'wt', encoding='utf-8') as target_file:
        target_file.write(contents)


def log_commandline(
    cwd: str,
    command: typing.Iterable[str],
) -> None:
    command_string = ' '.join(
        f'"{arg}"' if ' ' in arg else arg
        for arg in command
    )

    sys.stdout.write('\n')
    sys.stdout.write(colors.color(cwd, fg='blue'))
    sys.stdout.write(f' $ {command_string}\n')


def log_heading(heading: str) -> None:
    sys.stdout.write('=== ')
    sys.stdout.write(colors.color(heading, style='bold'))
    sys.stdout.write(' ===\n')


def log_output(output: str) -> None:
    sys.stdout.write('> ')
    sys.stdout.write(colors.color(f'{output.rstrip()}', fg='gray'))
    sys.stdout.write('\n')
