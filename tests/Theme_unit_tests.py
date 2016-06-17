import unittest


class ThemeUnitTests(unittest.TestCase):

    def test_initialisation(self):
        import jicagile.config
        themes = jicagile.config.Themes()
        self.assertEqual(len(themes), 0)

    def test_theme_member_initialisation(self):
        import jicagile.config
        theme = jicagile.config.Themes.Member("img", "bioimage analysis")
        self.assertEqual(theme.lookup, "img")
        self.assertEqual(theme.description, "bioimage analysis")

    def test_add_member_to_themes(self):
        import jicagile
        themes = jicagile.config.Themes()
        themes.add_member(lookup="img", description="bioimage analysis")
        self.assertEqual(len(themes), 1)
        self.assertTrue(isinstance(themes.member("img"), jicagile.config.Themes.Member))
