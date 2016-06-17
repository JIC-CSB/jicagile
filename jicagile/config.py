"""Module for dealing with configuration team, themes etc."""

import yaml


class Team(dict):
    """Class representing an agile team."""

    class Member(object):
        """Class representing a team member."""
        def __init__(self, lookup, first_name, last_name):
            self.lookup = lookup
            self.first_name = first_name
            self.last_name = last_name

    @classmethod
    def from_yaml(cls, yaml_str):
        """Return a team created from a yaml string."""
        data = yaml.load(yaml_str)
        team = cls()
        for item in data:
            team.add_member(**item)
        return team

    @classmethod
    def from_file(cls, fpath):
        """Return a team read in from file."""
        return cls.from_yaml(file(fpath))

    @property
    def lookups(self):
        """Return set of lookup aliases in the team."""
        return set(self.keys())

    def add_member(self, lookup, first_name, last_name):
        """Add a team member."""
        if lookup in self:
            raise(KeyError("Lookup {} already in use".format(lookup)))
        self[lookup] = self.Member(lookup, first_name, last_name)

    def member(self, lookup):
        """Return the team member associated with the lookup."""
        return self[lookup]


