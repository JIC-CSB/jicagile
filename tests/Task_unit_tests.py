import unittest

class TaskUnitTests(unittest.TestCase):

    def test_task_fname(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3)
        self.assertEqual(task.fname, "do-something-great.yml")

    def test_task_fpath(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3)
        self.assertEqual(task.fpath("/tmp"), "/tmp/do-something-great.yml")

    def test_task_can_be_initialised_with_primary_contact(self):
        import jicagile
        task = jicagile.Task(" Do something great! ", 3, primary_contact="TO")
        self.assertEqual(task["primary_contact"], "TO")

    def test_task_can_be_initialised_with_a_theme(self):
        import jicagile
        task = jicagile.Task("Do something great!", 3, theme="misc")
        self.assertEqual(task["theme"], "misc")


if __name__ == "__main__":
    unittest.main()
