"""Git integration tests."""

import unittest
import os
import os.path
import shutil
from subprocess import Popen, PIPE
import tempfile

import mock

CUR_DIR = os.getcwd()


class GitIntegrationTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(CUR_DIR)
        shutil.rmtree(self.tmp_dir)

    def test_edit_without_git(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        task_fpath = os.path.join(backlog_dir, "basic-task.yml")

        team = jicagile.config.Team()
        team.add_member("TO", "Tjelvar", "Olsson")
        team.add_member("MH", "Matthew", "Hartley")
        cli.project.team = team

        themes = jicagile.config.Themes()
        themes.add_member("admin", "grants, appraisals, etc")
        cli.project.themes = themes

        args = cli.parse_args(["edit",
                              task_fpath,
                              "-s", "3",
                              "-p", "TO",
                              "-e", "admin"])
        cli.run(args)

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Basic task")
        self.assertEqual(task_from_file["storypoints"], 3)
        self.assertEqual(task_from_file["primary_contact"], "TO")
        self.assertEqual(task_from_file["theme"], "admin")

    @mock.patch('subprocess.Popen')
    def test_edit_with_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = False  # We are not testing integration here.
            cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        task_fpath = os.path.join(backlog_dir, "basic-task.yml")


        args = cli.parse_args(["edit", task_fpath, "-s", "3"])
        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = True  # We are testing integration here.
            cli.run(args)
        patch_popen.assert_called_with(["git", "add", task_fpath])


    def test_edit_title_without_git(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        org_task_fpath = os.path.join(backlog_dir, "basic-task.yml")
        new_task_fpath = os.path.join(backlog_dir, "complicated-task.yml")

        self.assertTrue(os.path.isfile(org_task_fpath))
        self.assertFalse(os.path.isfile(new_task_fpath))

        args = cli.parse_args(["edit",
                              org_task_fpath,
                              "-t", "Complicated task"])
        cli.run(args)

        self.assertFalse(os.path.isfile(org_task_fpath))
        self.assertTrue(os.path.isfile(new_task_fpath))

        task_from_file = jicagile.Task.from_file(new_task_fpath)
        self.assertEqual(task_from_file["title"], "Complicated task")

    @mock.patch('subprocess.Popen')
    def test_edit_title_with_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = False  # Just creating a task to work with not testing git integration.
            cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        org_task_fpath = os.path.join(backlog_dir, "basic-task.yml")
        new_task_fpath = os.path.join(backlog_dir, "complicated-task.yml")

        self.assertTrue(os.path.isfile(org_task_fpath))
        self.assertFalse(os.path.isfile(new_task_fpath))

        args = cli.parse_args(["edit",
                              org_task_fpath,
                              "-t", "Complicated task"])
        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = True  # This is where we test git integration.
            cli.run(args)

        calls = [mock.call(["git", "add", org_task_fpath]),
                 mock.call(["git", "mv", org_task_fpath, new_task_fpath])]
        self.assertEqual(patch_popen.call_args_list, calls)

    def test_is_git_repo(self):
        from jicagile.cli import CLI
        cli = CLI()
        self.assertFalse(cli.is_git_repo)
        process = Popen(["git", "init"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        self.assertTrue(cli.is_git_repo)

    @mock.patch('subprocess.Popen')
    def test_add_without_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Simple task", "1"])

        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = False
            cli.run(args)
        patch_popen.assert_not_called()

    @mock.patch('subprocess.Popen')
    def test_add_with_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Simple task", "1"])

        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = True
            cli.run(args)
        fpath = os.path.join(".", "backlog", "simple-task.yml")
        patch_popen.assert_called_with(["git", "add", fpath])

    @mock.patch('subprocess.Popen')
    def test_theme_without_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["theme", "add", "admin", "stuff to do"])

        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = False
            cli.run(args)
        patch_popen.assert_not_called()

    @mock.patch('subprocess.Popen')
    def test_theme_with_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["theme", "add", "admin", "stuff to do"])

        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = True
            cli.run(args)
        fpath = os.path.join(".", ".theme.yml")
        patch_popen.assert_called_with(["git", "add", fpath])

    @mock.patch('subprocess.Popen')
    def test_mv_without_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["mv", "path/to/move", "/dest/"])

        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = False
            cli.run(args)
        patch_popen.assert_called_with(["mv", "path/to/move", "/dest/"])

    @mock.patch('subprocess.Popen')
    def test_mv_with_git(self, patch_popen):
        process_mock = mock.MagicMock()
        attrs = {"communicate.return_value": None}
        process_mock.configure(**attrs)
        patch_popen.return_value = process_mock
        from jicagile.cli import CLI
        cli = CLI()

        args = cli.parse_args(["mv", "path/to/move", "/dest/"])
        with mock.patch("jicagile.cli.CLI.is_git_repo", new_callable=mock.PropertyMock) as mock_is_git_repo:
            mock_is_git_repo.return_value = True
            cli.run(args)

        patch_popen.assert_called_with(["git", "mv", "path/to/move", "/dest/"])

