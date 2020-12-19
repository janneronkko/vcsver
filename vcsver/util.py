import typing


def parse_pkg_info_file(path: str) -> typing.Dict[str, str]:
    with open(path, 'rt') as pkg_info_file:
        return {
            key.strip(): value.strip()
            for key, value in (
                line.split(':', 1)
                for line in pkg_info_file
                if ':' in line
            )
        }
