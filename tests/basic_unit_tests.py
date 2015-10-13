import unittest

class BasicUnitTests(unittest.TestCase):

    def test_package_has_version_string(self):
        import jicagile
        self.assertTrue(isinstance(jicagile.__version__, str))


if __name__ == "__main__":
    unittest.main()
