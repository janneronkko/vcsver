import pathlib
import os
import subprocess
import typing

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

    command_string = ' '.join(
        f'"{arg}"' if ' ' in arg else arg
        for arg in cmd
    )
    cwd = kwargs.get('cwd', os.getcwd())
    print(f'\n{cwd} $ {command_string}')

    try:
        process = subprocess.run(cmd, **kwargs)  # pylint: disable=subprocess-run-check

        _print_output(process.stdout, process.stderr)

    except subprocess.CalledProcessError as err:
        _print_output(err.output, err.stderr)

        raise

    return process


def _print_output(stdout, stderr):
    output = stderr or stdout

    if not output:
        return

    for line in output.split('\n'):
        print(f'> {line.rstrip()}')


def render_template(
    template_name: str,
    dest: pathlib.Path,
    context: typing.Dict[str, typing.Any],
) -> None:
    template = mako.template.Template(
        filename=str(TEMPLATE_DIR / f'{template_name}.mako'),
    )

    contents = template.render(**context)

    print('=== {dest.name} ===')
    for line in contents.split('\n'):
        print(f'> {line.rstrip()}')

    with open(dest, 'wt', encoding='utf-8') as target_file:
        target_file.write(contents)
