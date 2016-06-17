"""jicagile package."""

import os
import os.path
from operator import itemgetter

import yaml
from slugify import slugify

__version__ = "0.0.4"


class Task(dict):
    """Task."""

    def __init__(self, title, storypoints, primary_contact=None):
        self["title"] = title
        self["storypoints"] = storypoints
        self["primary_contact"] = primary_contact

    @staticmethod
    def from_file(fpath):
        """Return a task read in from file."""
        data = yaml.load(file(fpath))
        return Task(**data)

    @property
    def fname(self):
        """Return the task file name."""
        return "{}.yml".format(slugify(self["title"]))

    def fpath(self, directory):
        """Return the task file path."""
        return os.path.join(directory, self.fname)


class TaskCollection(list):
    """Class for storing a collection of tasks."""

    @classmethod
    def from_directory(cls, directory):
        task_collection = cls()
        fpaths = [os.path.join(directory, fn)
                  for fn in os.listdir(directory)
                  if fn.endswith(".yml") or fn.endswith(".yaml")]
        for fp in fpaths:
            task_collection.append(Task.from_file(fp))
        return task_collection

    @property
    def primary_contacts(self):
        """Return set of primary contacts."""
        return sorted(set([item["primary_contact"] for item in self]))

    @property
    def storypoints(self):
        """Return the number of story points in the task collection."""
        return sum([item["storypoints"] for item in self])

    def tasks_for(self, primary_contact, sort_by="storypoints", reverse=False):
        """Return list of tasks for a primary contact."""
        key = itemgetter(sort_by)
        task_collection = TaskCollection()
        for task in sorted(self, key=key, reverse=reverse):
            if task["primary_contact"] == primary_contact:
                task_collection.append(task)
        return task_collection


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
        if os.path.isfile(fpath):
            return cls.from_yaml(file(fpath))
        else:
            return cls()

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


class Project(object):
    """Agile project management class."""

    def __init__(self, directory, team_fpath=".team.yml"):
        self.team = Team.from_file(team_fpath)
        self.directory = directory
        if not os.path.isdir(self.backlog_directory):
            os.mkdir(self.backlog_directory)
        if not os.path.isdir(self.current_sprint_directory):
            os.mkdir(self.current_sprint_directory)
        if not os.path.isdir(self.current_todo_directory):
            os.mkdir(self.current_todo_directory)
        if not os.path.isdir(self.current_done_directory):
            os.mkdir(self.current_done_directory)

    def __eq__(self, other):
        return self.directory == other.directory

    @property
    def backlog_directory(self):
        """Return the path to the backlog directory."""
        return os.path.join(self.directory, "backlog")

    @property
    def current_sprint_directory(self):
        """Return the path to the current sprint directory."""
        return os.path.join(self.directory, "current")

    @property
    def current_todo_directory(self):
        """Return the path to the current 'to do' directory."""
        return os.path.join(self.current_sprint_directory, "todo")

    @property
    def current_done_directory(self):
        """Return the path to the current 'done' directory."""
        return os.path.join(self.current_sprint_directory, "done")

    def add_task(self, title, storypoints,
                 primary_contact=None, current=False):
        """Add a task to the backlog."""
        task = Task(title, storypoints, primary_contact=primary_contact)
        directory = self.backlog_directory
        if current:
            directory = self.current_todo_directory
        with open(task.fpath(directory), "w") as fh:
            yaml.dump(task, fh, explicit_start=True, default_flow_style=False)
        return task

    def edit_task(self, fpath, title=None,
                  storypoints=None, primary_contact=None):
        """Edit an exiting task."""
        task = Task.from_file(fpath)
        if title is not None:
            task["title"] = title
        if storypoints is not None:
            task["storypoints"] = storypoints
        if primary_contact is not None:
            task["primary_contact"] = primary_contact
        with open(fpath, "w") as fh:
            yaml.dump(task, fh, explicit_start=True, default_flow_style=False)
        return task
