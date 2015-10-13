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

    def test_task_fname(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3)
        self.assertEqual(task.fname, "do-something-great.yml")

    def test_task_fpath(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3)
        self.assertEqual(task.fpath("/tmp"), "/tmp/do-something-great.yml")


class PrimaryContactUnitTests(unittest.TestCase):

    def test_task_can_be_initialised_with_primary_contact(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3, primary_contact="TO")
        self.assertEqual(task["primary_contact"], "TO")


class TaskCollectionUnitTests(unittest.TestCase):

    def test_initialisation(self):
        import jicagile
        task_collection = jicagile.TaskCollection()
        self.assertEqual(len(task_collection), 0)

    def test_primary_contacts_property(self):
        import jicagile
        task_collection = jicagile.TaskCollection()

        task1 = jicagile.Task("Do 1", 3, primary_contact="TO")
        task2 = jicagile.Task("Do 2", 3, primary_contact="MH")
        task3 = jicagile.Task("Do 3", 3, primary_contact="TO")

        task_collection.append(task1)
        task_collection.append(task2)
        task_collection.append(task3)

        self.assertEqual(len(task_collection), 3)
        self.assertEqual(task_collection.primary_contacts, set(["TO", "MH"]))

    def test_tasks_for_primary_contact(self):
        import jicagile
        task_collection = jicagile.TaskCollection()

        task1 = jicagile.Task("What 1", 1, primary_contact="TO")
        task2 = jicagile.Task("Do 2", 3, primary_contact="MH")
        task3 = jicagile.Task("Do 3", 3, primary_contact="TO")

        task_collection.append(task1)
        task_collection.append(task2)
        task_collection.append(task3)

        to_tasks = task_collection.tasks_for(primary_contact="TO",
                                             sort_by="title")
        self.assertEqual(len(to_tasks), 2)
        self.assertEqual(to_tasks[0]["title"], "Do 3")

        to_tasks = task_collection.tasks_for(primary_contact="TO",
                                             sort_by="title",
                                             reverse=True)
        self.assertEqual(len(to_tasks), 2)
        self.assertEqual(to_tasks[0]["title"], "What 1")

        to_tasks = task_collection.tasks_for(primary_contact="TO",
                                             sort_by="storypoints")
        self.assertEqual(len(to_tasks), 2)
        self.assertEqual(to_tasks[0]["title"], "What 1")

    def test_story_points(self):
        import jicagile
        task_collection = jicagile.TaskCollection()

        task1 = jicagile.Task("What 1", 1, primary_contact="TO")
        task2 = jicagile.Task("Do 2", 3, primary_contact="MH")
        task3 = jicagile.Task("Do 3", 5, primary_contact="TO")

        task_collection.append(task1)
        task_collection.append(task2)
        task_collection.append(task3)

        self.assertEqual(task_collection.storypoints, 9)

        to_tasks = task_collection.tasks_for(primary_contact="TO",
                                             sort_by="title",
                                             reverse=True)
        self.assertEqual(to_tasks.storypoints, 6)


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

        # It is also possible to add a task to the current sprint.
        task = project.add_task(u"Say hello now.", 1, primary_contact="TO", current=True)
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


if __name__ == "__main__":
    unittest.main()
