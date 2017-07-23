import collections
import unittest

from . import helpers
from .. import autover
from .. import errors
from .. import types


class HandleVersionTest(unittest.TestCase, helpers.MockMixin):
    def setUp(self):
        super().setUp()

        self.get_version_mock = self.patch(
            '{}.get_version'.format(autover.__name__),
            return_value=self.sentinel.version,
        )

        self.dist_mock = self.mock(name='Dist')
        self.dist_mock.use_autover = True
        self.dist_mock.metadata.version = None

    def test_disabled(self):
        self.dist_mock.use_autover = None
        autover.handle_version(self.dist_mock, self.sentinel.attr, self.sentinel.value)

        self.assertIsNone(self.dist_mock.metadata.version)
        self.assertFalse(self.get_version_mock.called)

    def test_use_autover_set_to_true(self):
        autover.handle_version(self.dist_mock, self.sentinel.attr, self.sentinel.value)

        self.assertIs(self.dist_mock.metadata.version, self.sentinel.version)

        self.get_version_mock.assert_called_once_with(**autover.DEFAULT_CONFIG)

    def test_empty_user_config(self):
        self.dist_mock.use_autover = {}
        autover.handle_version(self.dist_mock, self.sentinel.attr, self.sentinel.value)

        self.assertIs(self.dist_mock.metadata.version, self.sentinel.version)

        self.get_version_mock.assert_called_once_with(**autover.DEFAULT_CONFIG)

    def test_user_config(self):
        self.dist_mock.use_autover = {
            'root_version': '1.0',
        }
        autover.handle_version(self.dist_mock, self.sentinel.attr, self.sentinel.value)

        self.assertIs(self.dist_mock.metadata.version, self.sentinel.version)

        self.get_version_mock.assert_called_once_with(
            root_version='1.0',
            **{key: value for key, value in autover.DEFAULT_CONFIG.items() if key not in self.dist_mock.use_autover}
        )


class ConfigToGetVersionKwargsTest(unittest.TestCase, helpers.MockMixin):
    def test_empty_config(self):
        self.assertEqual(
            autover.config_to_get_version_kwargs({}),
            autover.DEFAULT_CONFIG,
        )

    def test_custom_config(self):
        custom_config = {
            'root_version': '1.0',
        }

        self.assertEqual(
            autover.config_to_get_version_kwargs(custom_config),
            collections.ChainMap(
                custom_config,
                autover.DEFAULT_CONFIG,
            ),
        )

    def test_unknown_item(self):
        self.assertRaises(
            errors.InvalidConfigError,
            autover.config_to_get_version_kwargs,
            {'unknown_item': 1},
        )


class GetVersionTest(unittest.TestCase, helpers.MockMixin):
    def setUp(self):
        super().setUp()

        self.root_version = self.sentinel.root_version

        self.read_revision_info_mock = self.mock(
            return_value=types.RevisionInfo(
                latest_tag=self.sentinel.latest_tag,
                distance=0,
                commit=self.sentinel.commit,
                dirty=False,
            ),
        )

        self.parse_tag_mock = self.mock(
            return_value=self.sentinel.latest_version,
        )

        self.create_version_mock = self.mock(
            return_value=self.sentinel.version,
        )

        self.parse_pkg_info_file_mock = self.patch(
            'setuptools_autover.util.parse_pkg_info_file',
            return_value={
                'Version': self.sentinel.pkg_info_version,
            },
        )

    def _get_version(self):
        return autover.get_version(
            root_version=self.root_version,
            read_revision_info=self.read_revision_info_mock,
            parse_tag=self.parse_tag_mock,
            create_version=self.create_version_mock,
        )

    def test_existing_version_info_using_callable(self):
        version = self._get_version()
        self.assertEqual(version, self.sentinel.version)

        self.read_revision_info_mock.assert_called_once_with()

        self.parse_tag_mock.assert_called_once_with(self.sentinel.latest_tag)

        self.create_version_mock.assert_called_once_with(unittest.mock.ANY)

        self.assertFalse(self.parse_pkg_info_file_mock.called)

    def test_no_tags(self):
        self.read_revision_info_mock.return_value = types.RevisionInfo(
            latest_tag=None,
            distance=10,
            commit=self.sentinel.commit,
            dirty=False,
        )

        version = self._get_version()
        self.assertEqual(version, self.sentinel.version)

        self.read_revision_info_mock.assert_called_once_with()

        self.assertFalse(self.parse_tag_mock.called)

        self.create_version_mock.assert_called_once_with(unittest.mock.ANY)

        self.assertFalse(self.parse_pkg_info_file_mock.called)

    def test_no_revision_info_available(self):
        self.read_revision_info_mock.return_value = None

        self.parse_pkg_info_file_mock.side_effect = FileNotFoundError

        self.assertRaises(
            errors.RevisionInfoNotFoundError,
            self._get_version,
        )

        self.assertTrue(self.read_revision_info_mock.called)

        self.assertFalse(self.parse_tag_mock.called)

        self.assertFalse(self.create_version_mock.called)

        self.parse_pkg_info_file_mock.assert_called_once_with('PKG-INFO')

    def test_revision_info_from_pkg_info_file(self):
        self.read_revision_info_mock.return_value = None

        version = self._get_version()
        self.assertEqual(version, self.sentinel.pkg_info_version)

        self.parse_pkg_info_file_mock.assert_called_once_with('PKG-INFO')

    def test_invalid_read_revision_info_argument(self):
        self.read_revision_info_mock = self.sentinel.read_revision_info

        self.assertRaises(
            TypeError,
            self._get_version,
        )

        self.assertFalse(self.parse_tag_mock.called)

        self.assertFalse(self.create_version_mock.called)

        self.assertFalse(self.parse_pkg_info_file_mock.called)
