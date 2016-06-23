import unittest
import os
import os.path
import shutil
import sys
from contextlib import contextmanager
from StringIO import StringIO
import re
from subprocess import Popen, PIPE
import tempfile

ansi_escape = re.compile(r'\x1b[^m]*m')

@contextmanager
def capture_sys_output():
    capture_out, capture_err = StringIO(), StringIO()
    current_out, current_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = capture_out, capture_err
        yield capture_out, capture_err
    finally:
        sys.stdout, sys.stderr = current_out, current_err


HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, 'data')
CUR_DIR = os.getcwd()


class BasicWorkflowFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)


    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_basic_workflow(self):
        import jicagile

        # When we start off a backlog directory has not yet been created.
        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        self.assertFalse(os.path.isdir(backlog_dir))

        # However, once a project is initialised such a directory is created.
        project = jicagile.Project(self.tmp_dir)
        self.assertTrue(os.path.isdir(backlog_dir))
        self.assertTrue(isinstance(project, jicagile.Project))

        # We can add a task to the backlog.
        task, fpath = project.add_task(u"Create agile tool.", 5)
        self.assertEqual(task["title"], u"Create agile tool.")
        self.assertEqual(task["storypoints"], 5)

        # The task has also been written to file.
        self.assertTrue(os.path.isfile(fpath))
        self.assertEqual(fpath,
                         os.path.join(backlog_dir,
                                      "create-agile-tool.yml"))

        # The task is in yaml file format.
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task, task_from_file)

        # It is possible to edit the task.
        task, new_fpath = project.edit_task(fpath, storypoints=1)
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["storypoints"], 1)
        self.assertEqual(task, task_from_file)
        self.assertEqual(fpath, new_fpath)

        task, new_fpath = project.edit_task(fpath, title="Create a fit-for-purpose agile tool")
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["title"],
                         "Create a fit-for-purpose agile tool")
        self.assertEqual(task, task_from_file)
        self.assertEqual(new_fpath,
                         os.path.join(backlog_dir,
                                      "create-a-fit-for-purpose-agile-tool.yml"))

        project.edit_task(fpath, primary_contact="TO")
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["primary_contact"], "TO")

        # It is also possible to add a task to the current sprint.
        task, fpath = project.add_task(u"Say hello now.", 1,
                                primary_contact="TO", current=True)
        self.assertEqual(task["title"], u"Say hello now.")
        self.assertEqual(task["storypoints"], 1)
        self.assertEqual(task["primary_contact"], "TO")

        # The task has also been written to file.
        self.assertTrue(os.path.isfile(fpath))
        self.assertEqual(fpath,
                         os.path.join(self.tmp_dir,
                                      "current",
                                      "todo",
                                      "say-hello-now.yml"))


class ProjectFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_project_initialisation(self):
        import jicagile

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        current_sprint_dir = os.path.join(self.tmp_dir, "current")
        current_todo_dir = os.path.join(self.tmp_dir, "current", "todo")
        current_done_dir = os.path.join(self.tmp_dir, "current", "done")
        self.assertFalse(os.path.isdir(backlog_dir))
        self.assertFalse(os.path.isdir(current_sprint_dir))
        self.assertFalse(os.path.isdir(current_todo_dir))
        self.assertFalse(os.path.isdir(current_done_dir))

        project = jicagile.Project(self.tmp_dir)
        self.assertEqual(project.directory, self.tmp_dir)
        self.assertEqual(project.backlog_directory,
                         os.path.join(self.tmp_dir, "backlog"))
        self.assertEqual(project.current_sprint_directory,
                         os.path.join(self.tmp_dir, "current"))
        self.assertEqual(project.current_todo_directory,
                         os.path.join(self.tmp_dir, "current", "todo"))
        self.assertEqual(project.current_done_directory,
                         os.path.join(self.tmp_dir, "current", "done"))

        self.assertTrue(os.path.isdir(backlog_dir))
        self.assertTrue(os.path.isdir(current_sprint_dir))
        self.assertTrue(os.path.isdir(current_todo_dir))
        self.assertTrue(os.path.isdir(current_done_dir))

    def test_creation_of_an_existing_project(self):
        import jicagile

        p1 = jicagile.Project(self.tmp_dir)
        p2 = jicagile.Project(self.tmp_dir)
        self.assertEqual(p1, p2)

    def test_team(self):
        import jicagile

        fpath = os.path.join(self.tmp_dir, "team.yml")
        with open(fpath, "w") as fh:
            fh.write("""---
- lookup: TO
  first_name: Tjelvar
  last_name: Olsson
- lookup: MH
  first_name: Matthew
  last_name: Hartley
""")

        project = jicagile.Project(self.tmp_dir, team_fpath=fpath)
        self.assertEqual(len(project.team), 2)
        self.assertEqual(project.team.lookups, set(["TO", "MH"]))

    def test_themes(self):
        import jicagile

        fpath = os.path.join(self.tmp_dir, "themes.yml")
        with open(fpath, "w") as fh:
            fh.write("""---
- lookup: admin
  description: general admin tasks
- lookup: sysadmin
  description: systems administraiton
""")

        project = jicagile.Project(self.tmp_dir, themes_fpath=fpath)
        self.assertEqual(len(project.themes), 2)
        self.assertEqual(project.themes.lookups, set(["admin", "sysadmin"]))



class TaskFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_from_file(self):
        import jicagile
        fpath = os.path.join(self.tmp_dir, "test.yml")
        with open(fpath, "w") as fh:
            fh.write("""---\ntitle: Test\nstorypoints: 3""")
        task = jicagile.Task.from_file(fpath)
        self.assertEqual(task["title"], "Test")
        self.assertEqual(task["storypoints"], 3)


class TeamFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_team_from_file(self):
        import jicagile
        fpath = os.path.join(self.tmp_dir, "team.yml")
        with open(fpath, "w") as fh:
            fh.write("""---
- lookup: TO
  first_name: Tjelvar
  last_name: Olsson
- lookup: MH
  first_name: Matthew
  last_name: Hartley
""")
        team = jicagile.config.Team.from_file(fpath)
        self.assertEqual(len(team), 2)
        self.assertEqual(team.lookups, set(["TO", "MH"]))


class TaskCollectionFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_from_directory(self):
        import jicagile
        project = jicagile.Project(self.tmp_dir)
        task1, fpath = project.add_task("Basic task", 1)
        task2, fpath = project.add_task("Complex task", 8)
        expected = jicagile.TaskCollection()
        expected.extend([task1, task2])

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        self.assertEqual(jicagile.TaskCollection.from_directory(backlog_dir),
                         expected)


class CLIFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(CUR_DIR)
        shutil.rmtree(self.tmp_dir)

    def test_add(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        task_fpath = os.path.join(backlog_dir, "basic-task.yml")
        self.assertTrue(os.path.isfile(task_fpath))

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Basic task")
        self.assertEqual(task_from_file["storypoints"], 1)

    def test_add_to_current(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "-c", "Basic task", "1"])
        cli.run(args)

        current_todo_dir = os.path.join(self.tmp_dir, "current", "todo")
        task_fpath = os.path.join(current_todo_dir, "basic-task.yml")
        self.assertTrue(os.path.isfile(task_fpath))

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Basic task")
        self.assertEqual(task_from_file["storypoints"], 1)

    def test_add_with_theme(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()

        themes = jicagile.config.Themes()
        themes.add_member("admin", "grants, appraisals, etc")
        cli.project.themes = themes

        args = cli.parse_args(["add", "Basic task", "1", "-e", "admin"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        task_fpath = os.path.join(backlog_dir, "basic-task.yml")
        self.assertTrue(os.path.isfile(task_fpath))

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["theme"], "admin")

    def test_edit(self):
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
                              "-t", "Complicated task",
                              "-s", "8",
                              "-p", "TO",
                              "-e", "admin"])
        cli.run(args)

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Complicated task")
        self.assertEqual(task_from_file["storypoints"], 8)
        self.assertEqual(task_from_file["primary_contact"], "TO")
        self.assertEqual(task_from_file["theme"], "admin")

    def test_list(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog")
        args = cli.parse_args(["list", backlog_dir])
        with capture_sys_output() as (stdout, stderr):
            cli.run(args)
            text = ansi_escape.sub('', stdout.getvalue())
            expected = """# BACKLOG [1]

## None's tasks [1]

[] Basic task [1]
"""
            self.assertEqual(text, expected, "\n" + text + expected)

        team = jicagile.config.Team()
        team.add_member("TO", "Tjelvar", "Olsson")
        team.add_member("MH", "Matthew", "Hartley")
        cli.project.team = team

        themes = jicagile.config.Themes()
        themes.add_member("admin", "forms etc")
        themes.add_member("fun", "programming etc")
        cli.project.themes = themes

        args = cli.parse_args(["add", "Have fun", "1",
                               "-p", "TO",
                               "-e", "fun",
                               "-c"])
        cli.run(args)
        args = cli.parse_args(["add", "Email people", "1",
                               "-p", "TO",
                               "-e", "admin",
                               "-c"])
        cli.run(args)
        args = cli.parse_args(["add", "Attempt to fill in appriasal form", "5",
                               "-p", "TO",
                               "-e", "admin",
                               "-c"])
        cli.run(args)
        args = cli.parse_args(["add", "Other stuff", "1",
                               "-p", "TO",
                               "-c"])
        cli.run(args)
        args = cli.parse_args(["add", "Management stuff", "8",
                               "-p", "MH",
                               "-e", "admin",
                               "-c"])
        cli.run(args)

        args = cli.parse_args(["list", "todo"])
        with capture_sys_output() as (stdout, stderr):
            cli.run(args)
            text = ansi_escape.sub("", stdout.getvalue())
            expected = """# TODO [16]

## Matthew's tasks [8]

[admin] Management stuff [8]

## Tjelvar's tasks [8]

[] Other stuff [1]
[admin] Email people [1]
[admin] Attempt to fill in appriasal form [5]
[fun] Have fun [1]
"""
            self.assertEqual(text, expected, "\n" + text + expected)

        args = cli.parse_args(["list", "todo", "-p", "TO"])
        with capture_sys_output() as (stdout, stderr):
            cli.run(args)
            text = ansi_escape.sub("", stdout.getvalue())
            expected = """# TODO [8]

## Tjelvar's tasks [8]

[] Other stuff [1]
[admin] Email people [1]
[admin] Attempt to fill in appriasal form [5]
[fun] Have fun [1]
"""
            self.assertEqual(text, expected, "\n" + text + expected)

        args = cli.parse_args(["list", "done"])
        with capture_sys_output() as (stdout, stderr):
            cli.run(args)
            text = ansi_escape.sub("", stdout.getvalue())
            expected = """# DONE [0]\n"""
            self.assertEqual(text, expected, "\n" + text + expected)

    def test_list_backlog_with_trailing_slash(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        backlog_dir = os.path.join(self.tmp_dir, "backlog/")
        args = cli.parse_args(["list", backlog_dir])
        with capture_sys_output() as (stdout, stderr):
            cli.run(args)
            text = ansi_escape.sub('', stdout.getvalue())
            expected = """# BACKLOG [1]

## None's tasks [1]

[] Basic task [1]
"""
            self.assertEqual(text, expected, "\n" + text + expected)

    def test_is_git_repo(self):
        from jicagile.cli import CLI
        cli = CLI()
        self.assertFalse(cli.is_git_repo)
        process = Popen(["git", "init"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        self.assertTrue(cli.is_git_repo)

    def test_mv(self):
        import jicagile
        from jicagile.cli import CLI
        cli = CLI()
        args = cli.parse_args(["add", "Basic task", "1"])
        cli.run(args)

        src_fpath = os.path.join("backlog", "basic-task.yml")
        todo = os.path.join("current", "todo")
        dest_fpath = os.path.join(todo, "basic-task.yml")

        self.assertTrue(os.path.isfile(src_fpath))

        args = cli.parse_args(["mv", src_fpath, todo])
        cli.run(args)

        self.assertFalse(os.path.isfile(src_fpath))
        self.assertTrue(os.path.isfile(dest_fpath))



class ThemesFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(CUR_DIR)
        shutil.rmtree(self.tmp_dir)

    def test_to_file(self):
        from jicagile.config import Themes
        fpath = os.path.join(self.tmp_dir, ".themes.yml")
        self.assertFalse(os.path.isfile(fpath))

        themes = Themes()
        themes.add_member("admin", "stuff we need to do")
        themes.to_file(fpath)
        self.assertTrue(os.path.isfile(fpath))
        from_file_themes = Themes.from_file(fpath)
        self.assertEqual(themes, from_file_themes)


    def test_theme_command(self):
        from jicagile.cli import CLI
        from jicagile.config import Themes
        cli = CLI()

        # No .themes.yml file exists yet.
        themes_fpath = os.path.join(self.tmp_dir, ".themes.yml")
        self.assertFalse(os.path.isfile(themes_fpath))

        args = cli.parse_args(["theme", "add", "admin", "stuff we need to do"])
        cli.run(args)
        self.assertTrue(os.path.isfile(themes_fpath))
        themes = Themes.from_file(themes_fpath)
        self.assertEqual(len(themes), 1)
        self.assertEqual(themes["admin"].description, "stuff we need to do")

        args = cli.parse_args(["theme", "add", "sysadmin", "configure servers"])
        cli.run(args)
        themes = Themes.from_file(themes_fpath)
        self.assertEqual(len(themes), 2)

        args = cli.parse_args(["theme", "rm", "admin"])
        cli.run(args)
        themes = Themes.from_file(themes_fpath)
        self.assertEqual(len(themes), 1)
        self.assertFalse("admin" in themes)
        self.assertTrue("sysadmin" in themes)

        args = cli.parse_args(["theme", "rm", "admin"])
        cli.run(args)

    def test_add_to_empty(self):
        from jicagile.cli import CLI
        from jicagile.config import Themes
        cli = CLI()

        # Add one to create the .theme.yml file.
        args = cli.parse_args(["theme", "add", "admin", "stuff we need to do"])
        cli.run(args)

        # Remove it to create an empty file.
        args = cli.parse_args(["theme", "rm", "admin"])
        cli.run(args)

        # Add something to the empty file.
        args = cli.parse_args(["theme", "add", "admin", "stuff we need to do"])
        cli.run(args)


class TeamMemberFunctionalTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        if not os.path.isdir(self.tmp_dir):
            os.mkdir(self.tmp_dir)
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(CUR_DIR)
        shutil.rmtree(self.tmp_dir)

    def test_to_file(self):
        from jicagile.config import Team
        fpath = os.path.join(self.tmp_dir, ".team.yml")
        self.assertFalse(os.path.isfile(fpath))

        team = Team()
        team.add_member("TO", "Tjelvar", "Olsson")
        team.to_file(fpath)
        self.assertTrue(os.path.isfile(fpath))
        from_file_team = Team.from_file(fpath)
        self.assertEqual(team, from_file_team)

    def test_teammember_command(self):
        from jicagile.cli import CLI
        from jicagile.config import Team
        cli = CLI()

        # No .themes.yml file exists yet.
        team_fpath = os.path.join(self.tmp_dir, ".team.yml")
        self.assertFalse(os.path.isfile(team_fpath))

        args = cli.parse_args(["teammember", "add", "TO", "Tjelvar", "Olsson"])
        cli.run(args)
        self.assertTrue(os.path.isfile(team_fpath))
        team = Team.from_file(team_fpath)
        self.assertEqual(len(team), 1)
        self.assertEqual(team["TO"].first_name, "Tjelvar")
        self.assertEqual(team["TO"].last_name, "Olsson")

        args = cli.parse_args(["teammember", "add", "MH", "Matthew",  "Hartley"])
        cli.run(args)
        team = Team.from_file(team_fpath)
        self.assertEqual(len(team), 2)

        args = cli.parse_args(["teammember", "rm", "TO"])
        cli.run(args)
        team = Team.from_file(team_fpath)
        self.assertEqual(len(team), 1)
        self.assertFalse("TO" in team)
        self.assertTrue("MH" in team)

        args = cli.parse_args(["teammember", "rm", "TO"])
        cli.run(args)


if __name__ == "__main__":
    unittest.main()
