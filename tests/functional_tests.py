import unittest
import os
import os.path
import shutil

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, 'data')
TMP_DIR = os.path.join(HERE, 'tmp')


class FunctionalTests(unittest.TestCase):

    def setUp(self):
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    def tearDown(self):
        shutil.rmtree(TMP_DIR)

    def test_basic_workflow(self):
        import jicagile

        # When we start off a backlog directory has not yet been created.
        backlog_dir = os.path.join(TMP_DIR, "backlog")
        self.assertFalse(os.path.isdir(backlog_dir))

        # However, once a project is initialised such a directory is created.
        project = jicagile.Project(TMP_DIR)
        self.assertTrue(os.path.isdir(backlog_dir))
        self.assertTrue(isinstance(project, jicagile.Project))

        # We can add a task to the backlog.
        task = project.add_task(u"Create agile tool.", 5)
        self.assertEqual(task["title"], u"Create agile tool.")
        self.assertEqual(task["storypoints"], 5)

        # The task has also been written to file.
        fpath = os.path.join(backlog_dir, "create-agile-tool.yml")
        self.assertTrue(os.path.isfile(fpath))

        # The task is in yaml file format.
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task, task_from_file)

        # It is possible to edit the task.
        project.edit_task(fpath, storypoints=1)
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["storypoints"], 1)
        project.edit_task(fpath, title="Create a fit-for-purpose agile tool")
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["title"],
                         "Create a fit-for-purpose agile tool")
        project.edit_task(fpath, primary_contact="TO")
        task_from_file = jicagile.Task.from_file(fpath)
        self.assertEqual(task_from_file["primary_contact"], "TO")

        # It is also possible to add a task to the current sprint.
        task = project.add_task(u"Say hello now.", 1,
                                primary_contact="TO", current=True)
        self.assertEqual(task["title"], u"Say hello now.")
        self.assertEqual(task["storypoints"], 1)
        self.assertEqual(task["primary_contact"], "TO")

        # The task has also been written to file.
        fpath = os.path.join(TMP_DIR, "current", "todo", "say-hello-now.yml")
        self.assertTrue(os.path.isfile(fpath))

    def test_project_initialisation(self):
        import jicagile

        backlog_dir = os.path.join(TMP_DIR, "backlog")
        current_sprint_dir = os.path.join(TMP_DIR, "current")
        current_todo_dir = os.path.join(TMP_DIR, "current", "todo")
        current_done_dir = os.path.join(TMP_DIR, "current", "done")
        self.assertFalse(os.path.isdir(backlog_dir))
        self.assertFalse(os.path.isdir(current_sprint_dir))
        self.assertFalse(os.path.isdir(current_todo_dir))
        self.assertFalse(os.path.isdir(current_done_dir))

        project = jicagile.Project(TMP_DIR)
        self.assertEqual(project.directory, TMP_DIR)
        self.assertEqual(project.backlog_directory,
                         os.path.join(TMP_DIR, "backlog"))
        self.assertEqual(project.current_sprint_directory,
                         os.path.join(TMP_DIR, "current"))
        self.assertEqual(project.current_todo_directory,
                         os.path.join(TMP_DIR, "current", "todo"))
        self.assertEqual(project.current_done_directory,
                         os.path.join(TMP_DIR, "current", "done"))

        self.assertTrue(os.path.isdir(backlog_dir))
        self.assertTrue(os.path.isdir(current_sprint_dir))
        self.assertTrue(os.path.isdir(current_todo_dir))
        self.assertTrue(os.path.isdir(current_done_dir))

    def test_creation_of_an_existing_project(self):
        import jicagile

        p1 = jicagile.Project(TMP_DIR)
        p2 = jicagile.Project(TMP_DIR)
        self.assertEqual(p1, p2)

    def test_from_file(self):
        import jicagile
        fpath = os.path.join(TMP_DIR, "test.yml")
        with open(fpath, "w") as fh:
            fh.write("""---\ntitle: Test\nstorypoints: 3""")
        task = jicagile.Task.from_file(fpath)
        self.assertEqual(task["title"], "Test")
        self.assertEqual(task["storypoints"], 3)

    def test_team_from_file(self):
        import jicagile
        fpath = os.path.join(TMP_DIR, "team.yml")
        with open(fpath, "w") as fh:
            fh.write("""---
- lookup: TO
  first_name: Tjelvar
  last_name: Olsson
- lookup: MH
  first_name: Matthew
  last_name: Hartley
""")
        team = jicagile.Team.from_file(fpath)
        self.assertEqual(len(team), 2)
        self.assertEqual(team.lookups, set(["TO", "MH"]))


class CLITests(unittest.TestCase):

    def setUp(self):
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    def tearDown(self):
        shutil.rmtree(TMP_DIR)

    def test_add(self):
        import jicagile
        from jicagile.cli import CLI
        args = CLI.parse_args(["add", "Basic task", "1"])
        cli = CLI(project_directory=TMP_DIR)
        cli.run_command("add", args)

        backlog_dir = os.path.join(TMP_DIR, "backlog")
        task_fpath = os.path.join(backlog_dir, "basic-task.yml")
        self.assertTrue(os.path.isfile(task_fpath))

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Basic task")
        self.assertEqual(task_from_file["storypoints"], 1)

    def test_add_to_current(self):
        import jicagile
        from jicagile.cli import CLI
        args = CLI.parse_args(["add", "-c", "Basic task", "1"])
        cli = CLI(project_directory=TMP_DIR)
        cli.run_command("add", args)

        current_todo_dir = os.path.join(TMP_DIR, "current", "todo")
        task_fpath = os.path.join(current_todo_dir, "basic-task.yml")
        self.assertTrue(os.path.isfile(task_fpath))

        task_from_file = jicagile.Task.from_file(task_fpath)
        self.assertEqual(task_from_file["title"], "Basic task")
        self.assertEqual(task_from_file["storypoints"], 1)

if __name__ == "__main__":
    unittest.main()
