import unittest
import os
import os.path
import shutil

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, 'data')
TMP_DIR = os.path.join(HERE, 'tmp')


class UnitTests(unittest.TestCase):

    def test_package_has_version_string(self):
        import jicagile
        self.assertTrue(isinstance(jicagile.__version__, str))


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

        # We can add a task.
        task = project.add_task(u"Create agile tool.", 5)
        self.assertEqual(task["title"], u"Create agile tool.")
        self.assertEqual(task["storypoints"], 5)

        # The task has also been written to file.
        fpath = os.path.join(backlog_dir, "create-agile-tool.yml")
        self.assertTrue(os.path.isfile(fpath))

        # The task is in yaml file format.
        task_from_file = jicagile.task_from_file(fpath)
        self.assertEqual(task, task_from_file)

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
        self.assertEqual(project.backlog_directory, os.path.join(TMP_DIR, "backlog"))
        self.assertEqual(project.current_sprint_directory, os.path.join(TMP_DIR, "current"))
        self.assertEqual(project.current_todo_directory, os.path.join(TMP_DIR, "current", "todo"))
        self.assertEqual(project.current_done_directory, os.path.join(TMP_DIR, "current", "done"))

        self.assertTrue(os.path.isdir(backlog_dir))
        self.assertTrue(os.path.isdir(current_sprint_dir))
        self.assertTrue(os.path.isdir(current_todo_dir))
        self.assertTrue(os.path.isdir(current_done_dir))

    def test_creation_of_an_existing_project(self):
        import jicagile

        p1 = jicagile.Project(TMP_DIR)
        p2 = jicagile.Project(TMP_DIR)
        self.assertEqual(p1, p2)

if __name__ == "__main__":
    unittest.main()
