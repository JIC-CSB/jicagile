"""jicagile package."""

import os
import os.path

import yaml
from slugify import slugify

__version__ = "0.0.1"


class Task(dict):
    """Task."""

    def __init__(self, title, storypoints):
        self["title"] = title
        self["storypoints"] = storypoints

    @staticmethod
    def from_file(fpath):
        """Return a task read in from file."""
        return yaml.load(file(fpath))

    @property
    def fname(self):
        """Return the task file name."""
        return "{}.yml".format(slugify(self["title"]))

    def fpath(self, directory):
        """Return the task file path."""
        return os.path.join(directory, self.fname)


class Project(object):
    """Agile project management class."""

    def __init__(self, directory):
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

    def add_task(self, title, storypoints, current=False):
        """Add a task to the backlog."""
        task = Task(title=title, storypoints=storypoints)
        directory = self.backlog_directory
        if current:
            directory = self.current_todo_directory
        with open(task.fpath(directory), "w") as fh:
            yaml.dump(task, fh, explicit_start=True, default_flow_style=False)
        return task
