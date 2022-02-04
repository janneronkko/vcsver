import typing

from . import (
    config,
    git,
    pep440,
    vcsver,
)


def finalize_distribution_options(dist: typing.Any) -> None:
    vcsver_config = config.read()

    source = vcsver_config.get('source')
    if source is None:
        return

    dist.metadata.version = vcsver.get_version(
        root_version='0',
        read_revision_info=git.GitRevisionInfoReader(),
        parse_tag=lambda tag: tag,
        create_version=pep440.post,
    )
