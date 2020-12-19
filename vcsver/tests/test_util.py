import io

from .. import util


def test_parsing_pkg_info_file(mocker):
    open_mock = mocker.patch('vcsver.util.open')
    open_mock.return_value = io.StringIO(
        'Name: name\n'
        'Version: 1.0\n'
    )

    pkg_info_data = util.parse_pkg_info_file(mocker.sentinel.path)

    open_mock = open_mock.assert_called_once_with(
        mocker.sentinel.path,
        'rt',
    )

    assert {
        'Name': 'name',
        'Version': '1.0',
    } == pkg_info_data
