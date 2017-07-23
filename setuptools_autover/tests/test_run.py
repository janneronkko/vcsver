import subprocess
import unittest

from . import helpers
from .. import run


class RunTest(unittest.TestCase, helpers.MockMixin):
    def setUp(self):
        super().setUp()

        self.stdout = b'stdout\n'
        self.stderr = b'stderr\n'

        self.process_mock = self.mock(
            name='Process',
            spec=subprocess.Popen,
        )
        self.process_mock.communicate.return_value = (self.stdout, self.stderr)
        self.process_mock.returncode = 0
        self.process_mock.stdout = self.sentinel.stdout_file
        self.process_mock.stderr = self.sentinel.stderr_file

        self.popen_mock = self.patch(
            'subprocess.Popen',
            name='Popen',
            return_value=self.process_mock,
        )

    def test_non_checked_successful_run(self):
        result = run.run(
            self.sentinel.cmd,
            self.sentinel.arg,
            check=False,
            kwarg=self.sentinel.kwarg,
        )

        self.popen_mock.assert_called_once_with(
            self.sentinel.cmd,
            self.sentinel.arg,
            kwarg=self.sentinel.kwarg,
        )

        self.assertIs(result, self.process_mock)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, self.stdout)
        self.assertEqual(result.stderr, self.stderr)

    def test_non_checked_unsuccessful_run(self):
        self.process_mock.returncode = 5

        result = run.run(
            self.sentinel.cmd,
            check=False,
        )

        self.popen_mock.assert_called_once_with(
            self.sentinel.cmd,
        )

        self.assertIs(result, self.process_mock)

        self.assertEqual(result.returncode, 5)
        self.assertEqual(result.stdout, self.stdout)
        self.assertEqual(result.stderr, self.stderr)

    def test_checked_successful_run(self):
        result = run.run(
            self.sentinel.cmd,
            check=True,
        )

        self.popen_mock.assert_called_once_with(
            self.sentinel.cmd,
        )

        self.assertIs(result, self.process_mock)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, self.stdout)
        self.assertEqual(result.stderr, self.stderr)

    def test_checked_unsuccessful_run(self):
        self.process_mock.returncode = 5

        with self.assertRaises(run.CalledProcessError) as context:
            run.run(
                self.sentinel.cmd,
                self.sentinel.arg1,
                self.sentinel.arg2,
                check=True,
                kwarg1=self.sentinel.kwarg1,
                kwarg2=self.sentinel.kwarg2,
            )

        self.popen_mock.assert_called_once_with(
            self.sentinel.cmd,
            self.sentinel.arg1,
            self.sentinel.arg2,
            kwarg1=self.sentinel.kwarg1,
            kwarg2=self.sentinel.kwarg2,
        )

        self.assertEqual(context.exception.returncode, 5)
        self.assertEqual(context.exception.stdout, self.stdout)
        self.assertEqual(context.exception.stderr, self.stderr)

        # Test that __str__ works by returning non-zero string
        self.assertTrue(str(context.exception))
