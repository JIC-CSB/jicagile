import unittest

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
        self.assertEqual(task_collection.primary_contacts, sorted(set(["TO", "MH"])))

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


if __name__ == "__main__":
    unittest.main()
