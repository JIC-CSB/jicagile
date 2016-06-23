"""jicagile package."""

import os
import os.path
from operator import itemgetter

import yaml
from slugify import slugify

from config import Team, Themes

__version__ = "0.4.0"


class Task(dict):
    """Task."""

    def __init__(self, title, storypoints, primary_contact=None, theme=None):
        self["title"] = title
        self["storypoints"] = storypoints
        self["primary_contact"] = primary_contact
        if theme:
            self["theme"] = theme
        else:
            self["theme"] = ""

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

    def tasks_for(self, primary_contact):
        """Return list of tasks for a primary contact."""
        key = itemgetter("theme", "storypoints")
        task_collection = TaskCollection()
        for task in sorted(self, key=key):
            if task["primary_contact"] == primary_contact:
                task_collection.append(task)
        return task_collection


class Project(object):
    """Agile project management class."""

    def __init__(self, directory, team_fpath=".team.yml", themes_fpath=".themes.yml"):
        self.team = Team()
        if os.path.isfile(team_fpath):
            self.team = Team.from_file(team_fpath)
        self.themes = Themes()
        if os.path.isfile(themes_fpath):
            self.themes = Themes.from_file(themes_fpath)

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

    def add_task(self,
                 title,
                 storypoints,
                 primary_contact=None,
                 theme=None,
                 current=False):
        """Add a task to the backlog.

        :returns: :class:`jicagile.Task` and fpath
        """
        task = Task(title, storypoints, primary_contact=primary_contact, theme=theme)
        directory = self.backlog_directory
        if current:
            directory = self.current_todo_directory
        fpath = task.fpath(directory)
        with open(fpath, "w") as fh:
            yaml.dump(task, fh, explicit_start=True, default_flow_style=False)
        return task, fpath

    def edit_task(self,
                  fpath,
                  title=None,
                  storypoints=None,
                  primary_contact=None,
                  theme=None):
        """Edit an exiting task.

        If the title is changed the fpath returned is the suggested new name of
        the file. However, the changes are made to the old file name and it is
        up to the caller to make the change to the file name.

        :returns: :class:`jicagile.Task` and fpath
        """
        task = Task.from_file(fpath)
        new_fpath = fpath
        if title is not None:
            task["title"] = title
            directory = os.path.dirname(fpath)
            new_fpath = task.fpath(directory)
        if storypoints is not None:
            task["storypoints"] = storypoints
        if primary_contact is not None:
            task["primary_contact"] = primary_contact
        if theme is not None:
            task["theme"] = theme
        with open(fpath, "w") as fh:
            yaml.dump(task, fh, explicit_start=True, default_flow_style=False)
        return task, new_fpath
