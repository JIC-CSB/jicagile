"""Command line interface unit tests."""

import unittest
import sys
from contextlib import contextmanager
from StringIO import StringIO

from mock import MagicMock


@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err


class RunCommandTest(unittest.TestCase):

    def test_run_command(self):
        from jicagile.cli import CLI
        cli = CLI()
        cli.dummy = MagicMock()
        cli.run_command("dummy", "the args")
        cli.dummy.assert_called_once_with("the args")


class AddCommandUnitTests(unittest.TestCase):

    def test_basic_usage(self):
        from jicagile.cli import CLI
        args = CLI.parse_args(["add", "Simple task", "1"])
        self.assertEqual(args.command, "add")
        self.assertEqual(args.title, "Simple task")
        self.assertEqual(args.storypoints, 1)
        self.assertFalse(args.current)

    def test_valid_storypoint_choices(self):
        from jicagile.cli import CLI

        for s in [1, 3, 5, 8]:
            args = CLI.parse_args(["add", "Simple task", str(s)])
            self.assertEqual(args.storypoints, s)

        for s in [2, 4, 6, 7, 9]:
            with self.assertRaises(SystemExit):
                with capture_sys_output() as (stdout, stderr):
                    args = CLI.parse_args(["add", "Simple task", str(s)])

    def test_primary_contact(self):
        from jicagile.cli import CLI
        args = CLI.parse_args(["add", "Simple task", "1", "-p", "TO"])
        self.assertEqual(args.primary_contact, "TO")

    def test_current(self):
        from jicagile.cli import CLI
        args = CLI.parse_args(["add", "-c", "Simple task", "1"])
        self.assertTrue(args.current)


class EditCommandUnitTests(unittest.TestCase):

    def test_basic_usage(self):
        from jicagile.cli import CLI
        args = CLI.parse_args(["edit", "fpath",
                               "-t", "Simple task",
                               "-s", "1",
                               "-p", "TO"])
        self.assertEqual(args.command, "edit")
        self.assertEqual(args.fpath, "fpath")
        self.assertEqual(args.title, "Simple task")
        self.assertEqual(args.storypoints, 1)
        self.assertEqual(args.primary_contact, "TO")


if __name__ == "__main__":
    unittest.main()
