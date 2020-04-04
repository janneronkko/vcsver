import unittest

import pkg_resources

from .. import pep440
from .. import types


class TestCreateVersionPostWithDev(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.create_version_string = pep440.create_post_with_dev

    def test_version_string_generation(self):
        ver = types.VersionInfo

        for data, expected_version in (
            (ver(latest_release='1.0', distance=0, commit='abcdef', dirty=False), '1.0'),
            (ver(latest_release='1.0', distance=0, commit='abcdef', dirty=True), '1.0+dirty'),
            (ver(latest_release='1.0', distance=1, commit='abcdef', dirty=False), '1.0.post0.dev1+abcdef'),
            (ver(latest_release='1.0', distance=1, commit='abcdef', dirty=True), '1.0.post0.dev1+abcdef.dirty'),
        ):
            with self.subTest(data):
                version = self.create_version_string(data)

                self.assertEqual(version, expected_version)


class VersionComparisonAssumptionsTest(unittest.TestCase):
    def test_assumptions(self):
        versions = iter((
            '1.0',
            '1.0.post0.dev1',
            '1.1.dev0',
            '1.1',
            '1.1+dirty',
            '1.1.post0.dev1+abcdef.dirty',
        ))

        prev_version = next(versions)
        for curr_version in versions:
            with self.subTest(prev_version=prev_version, curr_version=curr_version):
                ver1 = pkg_resources.parse_version(prev_version)
                ver2 = pkg_resources.parse_version(curr_version)

                self.assertLess(ver1, ver2)

            prev_version = curr_version
