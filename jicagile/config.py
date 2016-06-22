"""Module for dealing with configuration team, themes etc."""

import yaml

class _Config(dict):
    """Class representing a configuration."""

    @classmethod
    def from_yaml(cls, yaml_str):
        """Return a configuration created from a yaml string."""
        data = yaml.load(yaml_str)
        conf = cls()
        if data is None:
            return conf
        for item in data:
            conf.add_member(**item)
        return conf

    @classmethod
    def from_file(cls, fpath):
        """Return a configuration read in from file."""
        return cls.from_yaml(file(fpath))

    @property
    def lookups(self):
        """Return set of lookup aliases in the configuration."""
        return set(self.keys())

    def add_member(self, *args, **kwargs):
        """Add a configuration member."""
        lookup = None
        if "lookup" in kwargs:
            lookup = kwargs["lookup"]
        elif len(args) > 0:
            lookup = args[0]
        else:
            raise(RuntimeError("No lookup provided"))
        if lookup in self:
            raise(KeyError("Lookup {} already in use".format(lookup)))
        self[lookup] = self.Member(*args, **kwargs)

    def member(self, lookup):
        """Return the configuration member associated with the lookup."""
        return self[lookup]


class Team(_Config):
    """Class representing an agile team."""

    class Member(object):
        """Class representing a team member."""
        def __init__(self, lookup, first_name, last_name):
            self.lookup = lookup
            self.first_name = first_name
            self.last_name = last_name

        def __eq__(self, other):
            return (self.lookup == other.lookup) and (self.first_name == other.first_name) and (self.last_name == other.last_name)


    def name(self, lookup):
        if lookup in self:
            return self[lookup].first_name
        return lookup

    def to_file(self, fpath):
        """Write a configuration to file."""
        with open(fpath, "w") as fh:
            fh.write("---\n")
            for m in self.values():
                fh.write("- lookup: {}\n".format(m.lookup))
                fh.write("  first_name: {}\n".format(m.first_name))
                fh.write("  last_name: {}\n".format(m.last_name))


class Themes(_Config):
    """Class representing an collection of themes."""

    class Member(object):
        """Class representing a theme."""

        def __eq__(self, other):
            return (self.lookup == other.lookup) and (self.description == other.description)

        def __init__(self, lookup, description):
            self.lookup = lookup
            self.description = description

    def to_file(self, fpath):
        """Write a configuration to file."""
        with open(fpath, "w") as fh:
            fh.write("---\n")
            for m in self.values():
                fh.write("- lookup: {}\n".format(m.lookup))
                fh.write("  description: {}\n".format(m.description))
