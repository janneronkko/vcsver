import io
import unittest
from unittest import mock

from .. import util


class ParsePkgInfoFileTest(unittest.TestCase):
    def test_parsing(self):
        file_obj = io.StringIO(
            'Name: name\n'
            'Version: 1.0\n'
        )

        with mock.patch('setuptools_autover.util.open', mock.Mock(return_value=file_obj), create=True) as mock_open:
            pkg_info_data = util.parse_pkg_info_file(mock.sentinel.path)

        mock_open.assert_called_once_with(mock.sentinel.path, 'rt')

        self.assertEqual(
            pkg_info_data,
            {
                'Name': 'name',
                'Version': '1.0',
            },
        )
