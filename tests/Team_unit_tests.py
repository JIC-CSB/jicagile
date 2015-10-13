import unittest


class TeamUnitTests(unittest.TestCase):

    def test_initialisation(self):
        import jicagile
        team = jicagile.Team()
        self.assertEqual(len(team), 0)

    def test_team_member_initialisation(self):
        import jicagile
        team_member = jicagile.Team.Member("TO", "Tjelvar", "Olsson")
        self.assertEqual(team_member.lookup, "TO")
        self.assertEqual(team_member.first_name, "Tjelvar")
        self.assertEqual(team_member.last_name, "Olsson")

    def test_add_team_member(self):
        import jicagile
        team = jicagile.Team()
        team.add_member(lookup="TO", first_name="Tjelvar", last_name="Olsson")
        self.assertEqual(len(team), 1)
        self.assertTrue(isinstance(team.member("TO"), jicagile.Team.Member))

if __name__ == "__main__":
    unittest.main()
